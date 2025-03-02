import torch
import pandas as pd
import json
import joblib
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import train_test_split
from transformers import BertTokenizerFast, BertModel, BertPreTrainedModel
from torch.utils.data import Dataset, DataLoader
from torch import nn
from torch.cuda.amp import GradScaler, autocast

# 数据预处理
df = pd.read_csv("question.csv", encoding="gbk")  # 示例数据格式：question,tags,difficulty
# df = pd.read_json("question.json")
mlb = MultiLabelBinarizer()
tags_encoded = mlb.fit_transform(df['tags'].str.split(','))
difficulty_map = {"简单": 0, "中等": 1, "困难": 2}
df['difficulty'] = df['difficulty'].map(difficulty_map)
train_df, val_df = train_test_split(df, test_size=0.2, stratify=df['difficulty'])


# 自定义数据集
class MathDataset(Dataset):
    def __init__(self, df, tokenizer, max_len=128):
        self.df = df
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __getitem__(self, idx):
        data = self.df.iloc[idx]
        encoding = self.tokenizer(
            data['question'],
            max_length=self.max_len,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'tags': torch.FloatTensor(tags_encoded[idx]),
            'difficulty': torch.tensor(data['difficulty'])
        }


# 多任务BERT模型
class MathBERTMultiTask(BertPreTrainedModel):
    def __init__(self, config, num_tags, num_difficulty):
        super().__init__(config)
        self.bert = BertModel(config)
        self.tag_classifier = nn.Sequential(
            nn.Linear(config.hidden_size, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_tags)
        )
        self.difficulty_classifier = nn.Sequential(
            nn.Linear(config.hidden_size, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, num_difficulty)
        )

    def forward(self, input_ids, attention_mask, tags=None, difficulty=None):
        outputs = self.bert(input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output

        tag_logits = self.tag_classifier(pooled_output)
        difficulty_logits = self.difficulty_classifier(pooled_output)

        loss = None
        if tags is not None and difficulty is not None:
            loss_fn1 = nn.BCEWithLogitsLoss()
            loss_fn2 = nn.CrossEntropyLoss()
            loss = 0.7 * loss_fn1(tag_logits, tags) + 0.3 * loss_fn2(difficulty_logits, difficulty)
        return {'tag_logits': tag_logits, 'difficulty_logits': difficulty_logits, 'loss': loss}


# 训练配置
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = BertTokenizerFast.from_pretrained("bert-base-chinese")
model = MathBERTMultiTask.from_pretrained(
    "bert-base-chinese",
    num_tags=len(mlb.classes_),
    num_difficulty=3
).to(device)

train_loader = DataLoader(MathDataset(train_df, tokenizer), batch_size=32, shuffle=True)
optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)
scaler = GradScaler()

# 训练循环
for epoch in range(5):
    model.train()
    total_loss = 0
    for batch in train_loader:
        optimizer.zero_grad()
        with autocast():
            outputs = model(
                input_ids=batch['input_ids'].to(device),
                attention_mask=batch['attention_mask'].to(device),
                tags=batch['tags'].to(device),
                difficulty=batch['difficulty'].to(device)
            )
        scaler.scale(outputs['loss']).backward()
        scaler.step(optimizer)
        scaler.update()
        total_loss += outputs['loss'].item()
    print(f"Epoch {epoch + 1} Loss: {total_loss / len(train_loader):.4f}")

# 保存模型
model.save_pretrained("./math_bert_model")
tokenizer.save_pretrained("./math_bert_tokenizer")
joblib.dump(mlb, "./math_bert_model/tag_encoder.pkl")
