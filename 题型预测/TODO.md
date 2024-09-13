### 题目识别与分类相关

#### 识别
1. 使用了pix2tex，PIL.image转为二值图像后效果良好
2. pix2tex只适用于图片中有且仅有公式的情况，需要从图片中分离公式块与文字，同时保证顺序无异常
3. 从题号分割题目块，腾讯官网有个ai 
[试题识别](https://hiflow.tencent.com/document/applications/ocr-examination/#%E5%BA%94%E7%94%A8%E4%BB%8B%E7%BB%8D)

#### 分类
1. KNN or other
2. 题面与公式放不到一起，或者不提取公式

### 记录
+ 使用pix2tex生成公式，渲染公式并与生成内容比较，达到分割目的
+ 翻译成英文pix2tex就能识别, 提取英文再翻译回来 (upd 2024-9-13)
 ->  不能用
+ 