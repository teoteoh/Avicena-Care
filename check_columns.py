import pandas as pd

df = pd.read_csv('data/Dataset.csv', nrows=1)
print("Colunas do Dataset:")
for col in df.columns:
    print(f"  - {col}")
