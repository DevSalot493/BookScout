from flask import Flask, render_template, request, redirect, url_for
import requests
import os
import csv
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from preprocess_cache import preprocess_last_row
from ml_engine import get_similar_books

load_dotenv()
API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

app = Flask(__name__)
CACHE_FILE = "cache/book_data.csv"

# ✅ Genre list for checkbox filter
CANDIDATE_GENRES = [
    "Fantasy", "Science Fiction", "Horror", "Dystopian", "Adventure", "Classic",
    "Young Adult", "Historical Fiction", "Romance", "Coming-of-age", "Satire",
    "Thriller", "Mystery", "Philosophical Fiction", "Drama", "Self-help",
    "Non-fiction", "Memoir", "Fiction", "Non-Fiction", "Biography",
    "Literary Fiction", "Young-Adult Novel"
]

# Ensure cache directory exists
os.makedirs("cache", exist_ok=True)

def get_cached_book(title):
    """Return the cached row dict for `title`, or None."""
    if not os.path.exists(CACHE_FILE):
        return None
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["title"].strip().lower() == title.strip().lower():
                print(f"✅ Found cached book: {row['title']}")
                return row
    print("❌ Book not found in cache")
    return None

def save_to_cache(book):
    """
    Append a new book dict to the CSV if its title isn't already present.
    Expects keys: title, author, description, clean_description, categories, rating
    """
    existing = set()
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing.add(row["title"].lower())

    if book["title"].lower() in existing:
        print(f"⚠️ Duplicate not saved: {book['title']}")
        return

    file_exists = os.path.isfile(CACHE_FILE)
    with open(CACHE_FILE, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=book.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(book)
        print(f"💾 Book cached: {book['title']}")

def clean_description(text):
    """Strip HTML tags from text."""
    if not text:
        return ""
    return BeautifulSoup(text, "html.parser").get_text().strip()

def fetch_book_from_api(title):
    """
    Fetch metadata from Google Books; fall back to Wikipedia if needed.
    Returns a dict matching the CSV schema.
    """
    params = {"q": f"intitle:{title}", "maxResults": 1}
    if API_KEY:
        params["key"] = API_KEY
    data = requests.get("https://www.googleapis.com/books/v1/volumes", params=params).json()

    if "items" not in data:
        return None

    info = data["items"][0]["volumeInfo"]
    book_title = info.get("title", "")
    authors = ", ".join(info.get("authors", []))
    raw_desc = info.get("description", "")
    clean_desc = clean_description(raw_desc)
    categories = ", ".join(info.get("categories", []))
    rating = info.get("averageRating", "N/A")

    # If Google description is weak, Wikipedia fallback happens in preprocess_last_row()
    book = {
        "title": book_title,
        "author": authors,
        "description": raw_desc,
        "clean_description": clean_desc,
        "categories": categories,
        "rating": rating
    }

    save_to_cache(book)
    return book

@app.route("/", methods=["GET", "POST"])
def index():
    book_data = None
    # capture any checked genres
    selected_genres = request.form.getlist("genres") if request.method == "POST" else []

    if request.method == "POST":
        title = request.form["title"].strip()
        print(f"\n🔍 User searched for: {title}")

        book_data = get_cached_book(title)
        if not book_data:
            book_data = fetch_book_from_api(title)
            if book_data:
                preprocess_last_row()

        if book_data:
            # pass checked genres along via query string
            return redirect(
                url_for('recommend',
                        title=book_data['title'],
                        genres=",".join(selected_genres))
            )

    # render index with genre checkboxes
    return render_template(
        "index.html",
        candidate_genres=CANDIDATE_GENRES,
        selected_genres=selected_genres
    )

@app.route("/recommend")
def recommend():
    title = request.args.get("title")
    # Reconstruct genre list from query string
    genre_filter = (
        [g for g in request.args.get("genres", "").split(",") if g]
        if request.args.get("genres")
        else []
    )

    if not title:
        return redirect(url_for("index"))

    # Directly get top 5 *within* the chosen genres
    recommendations = get_similar_books(
        title,
        filter_genres=genre_filter,
        top_n=5
    )

    return render_template(
        "results.html",
        title=title,
        recommendations=recommendations,
        genre_filter=genre_filter
    )


if __name__ == "__main__":
    app.run(debug=True)
