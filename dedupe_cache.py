import pandas as pd

df = pd.read_csv("cache/book_data.csv")
df = df.drop_duplicates(subset="title", keep="first")
df.to_csv("cache/book_data.csv", index=False)

print("✅ Duplicates removed from CSV")
