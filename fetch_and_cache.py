from app import fetch_book_from_api, save_to_cache
from preprocess_cache import preprocess_last_row

def fetch_and_cache(title):
    book = fetch_book_from_api(title)
    if book:
        save_to_cache(book)
    return book
