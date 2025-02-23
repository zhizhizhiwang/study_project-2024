import pandas as pd

df = pd.read_parquet("hf://datasets/ALmonster/MATH-Hard-Chinese/math-hard-zh.parquet")

print(df)

