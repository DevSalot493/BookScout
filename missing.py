import pandas as pd

df = pd.read_csv("cache/book_data.csv")

missing_genres = df[df["categories"].isna() | (df["categories"].str.strip() == "")]

if missing_genres.empty:
    print("✅ All books have genres.")
else:
    print("❌ Books missing genres:")
    for i, row in missing_genres.iterrows():
        print(f"  - {row['title']} (Row {i})")
