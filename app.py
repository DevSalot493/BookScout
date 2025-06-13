from flask import Flask, render_template, request
import requests
import os
import csv
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load API key if available
load_dotenv()
API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

app = Flask(__name__)
CACHE_FILE = "cache/book_data.csv"

# Ensure cache directory exists
os.makedirs("cache", exist_ok=True)

# Check if book exists in cache
def get_cached_book(title):
    if not os.path.exists(CACHE_FILE):
        return None
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["title"].lower() == title.lower():
                return row
    return None

# Save book to cache
def save_to_cache(book):
    file_exists = os.path.isfile(CACHE_FILE)
    with open(CACHE_FILE, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=book.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(book)

# Clean description using BeautifulSoup
def clean_description(text):
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text().strip()

# Fetch book from API
def fetch_book_from_api(title):
    params = {
        "q": f"intitle:{title}",
        "maxResults": 1
    }
    if API_KEY:
        params["key"] = API_KEY
    response = requests.get("https://www.googleapis.com/books/v1/volumes", params=params)
    data = response.json()

    if "items" not in data:
        return None

    book_info = data["items"][0]["volumeInfo"]
    title = book_info.get("title", "")
    authors = ", ".join(book_info.get("authors", []))
    description = book_info.get("description", "")
    categories = ", ".join(book_info.get("categories", []))
    rating = book_info.get("averageRating", "N/A")

    clean_desc = clean_description(description)

    book = {
        "title": title,
        "author": authors,
        "description": description,
        "clean_description": clean_desc,
        "categories": categories,
        "rating": rating
    }

    save_to_cache(book)
    return book

@app.route("/", methods=["GET", "POST"])
def index():
    book_data = None
    if request.method == "POST":
        title = request.form["title"]
        book_data = get_cached_book(title)
        if not book_data:
            book_data = fetch_book_from_api(title)
    return render_template("index.html", book=book_data)

if __name__ == "__main__":
    app.run(debug=True)
    
