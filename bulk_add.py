#!/usr/bin/env python3
"""
bulk_add.py

Fetches a list of book titles from Google Books (with Wikipedia fallback)
and adds them to cache/book_data.csv (running preprocess_last_row on each).
"""

import time
from fetch_and_cache import fetch_and_cache   # helper: fetch → save CSV
from preprocess_cache import preprocess_last_row

# 📚 List your seed titles here (100 classics, sci-fi, modern favorites):
EXTRA_TITLES = [
    "1984",
    "Brave New World",
    "Fahrenheit 451",
    "Dune",
    "The Hobbit",
    "The Lord of the Rings",
    "The Catcher in the Rye",
    "To Kill a Mockingbird",
    "The Great Gatsby",
    "Pride and Prejudice",
    "Jane Eyre",
    "Wuthering Heights",
    "Moby Dick",
    "War and Peace",
    "Crime and Punishment",
    "The Brothers Karamazov",
    "Anna Karenina",
    "Les Misérables",
    "The Odyssey",
    "The Iliad",
    "The Divine Comedy",
    "Ulysses",
    "Don Quixote",
    "One Hundred Years of Solitude",
    "The Sound and the Fury",
    "Lolita",
    "Beloved",
    "The Kite Runner",
    "The Book Thief",
    "The Chronicles of Narnia",
    "Animal Farm",
    "Frankenstein",
    "Dracula",
    "The Picture of Dorian Gray",
    "The Stranger",
    "Catch-22",
    "Slaughterhouse-Five",
    "Ender's Game",
    "Neuromancer",
    "Snow Crash",
    "Foundation",
    "The Left Hand of Darkness",
    "Do Androids Dream of Electric Sheep?",
    "The Hitchhiker's Guide to the Galaxy",
    "Ready Player One",
    "A Clockwork Orange",
    "The Martian",
    "American Gods",
    "The Handmaid's Tale",
    "The Stand",
    "It",
    "The Shining",
    "Misery",
    "The Girl with the Dragon Tattoo",
    "Gone Girl",
    "The Da Vinci Code",
    "Angels & Demons",
    "The Alchemist",
    "Life of Pi",
    "The Giver",
    "The Hunger Games",
    "Catching Fire",
    "Mockingjay",
    "Divergent",
    "The Maze Runner",
    "The Fault in Our Stars",
    "Looking for Alaska",
    "The Perks of Being a Wallflower",
    "The Help",
    "Water for Elephants",
    "The Goldfinch",
    "A Game of Thrones",
    "A Clash of Kings",
    "A Storm of Swords",
    "A Feast for Crows",
    "A Dance with Dragons",
    "The Name of the Wind",
    "The Wise Man's Fear",
    "Mistborn: The Final Empire",
    "The Way of Kings",
    "Words of Radiance",
    "Shadow & Bone",
    "Six of Crows",
    "The Lies of Locke Lamora",
    "The City of Stairs",
    "The Priory of the Orange Tree",
    "Circe",
    "The Song of Achilles",
    "Normal People",
    "Eleanor Oliphant Is Completely Fine",
    "The Night Circus",
    "The Time Traveler's Wife",
    "The Book of Lost Things",
    "The Ocean at the End of the Lane",
    "Coraline",
    "Good Omens",
    "Sapiens: A Brief History of Humankind",
    "Educated"
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
