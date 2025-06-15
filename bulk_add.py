#!/usr/bin/env python3
"""
bulk_add.py

Fetches a list of book titles from Google Books (with Wikipedia fallback)
and adds them to cache/book_data.csv (running preprocess_last_row on each).
"""

import time
from preprocess_cache import preprocess_last_row
from app import fetch_book_from_api, save_to_cache
from preprocess_cache import preprocess_last_row

def fetch_and_cache(title):
    book = fetch_book_from_api(title)
    if book:
        save_to_cache(book)
    return book


# 📚 List your seed titles here (100 classics, sci-fi, modern favorites):
EXTRA_TITLES = [

]

def main():
    print(f"🚀 Starting bulk add of {len(EXTRA_TITLES)} titles...\n")
    for title in EXTRA_TITLES:
        print(f"🔍 Processing: {title}")
        book = fetch_and_cache(title)
        if book:
            print(f"  ➕ Cached: {book['title']}")
            preprocess_last_row()
        else:
            print(f"  ⚠️  Failed: {title}")
        # be kind to APIs
        time.sleep(1.0)
    print("\n✅ Bulk add complete!")

if __name__ == "__main__":
    main()