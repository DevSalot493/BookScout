#!/usr/bin/env python3
# clean_categories.py

import pandas as pd
import re

CACHE_FILE = "cache/book_data.csv"

def clean_category_list(cat_str):
    """
    Given a comma‑separated category string, drop any entry that
    contains no alphanumeric characters (e.g. '(' or ')' alone).
    """
    parts = [c.strip() for c in cat_str.split(',')]
    # Keep only parts that have at least one letter or digit
    cleaned = [c for c in parts if re.search(r'\w', c)]
    return ", ".join(cleaned)

def main():
    df = pd.read_csv(CACHE_FILE)
    if 'categories' not in df.columns:
        print("No 'categories' column found.")
        return

    # Apply cleaning to every row
    df['categories'] = df['categories'].fillna('').apply(clean_category_list)

    # Save back
    df.to_csv(CACHE_FILE, index=False)
    print(f"✅ Cleaned categories in {len(df)} rows and saved to {CACHE_FILE}")

if __name__ == "__main__":
    main()
