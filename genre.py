import csv
from collections import Counter

CSV_PATH = "cache/book_data.csv"
OUTPUT_CSV = "normalized_genre_counts.csv"
OUTPUT_OPTIONS = "genre_options.html"

def normalize(genre):
    # strip whitespace, lower, then title-case each word
    return genre.strip().lower().title()

def count_genres(csv_path):
    counter = Counter()
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cats = row.get("categories", "")
            for cat in cats.split(","):
                n = normalize(cat)
                if n:
                    counter[n] += 1
    return counter

if __name__ == "__main__":
    counts = count_genres(CSV_PATH)

    # Save counts to CSV
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Genre", "Count"])
        for genre, cnt in counts.most_common():
            writer.writerow([genre, cnt])

    # Generate HTML <option> tags
    with open(OUTPUT_OPTIONS, "w", encoding="utf-8") as f:
        for genre, cnt in counts.most_common():
            # HTML-escape genre if needed (here assuming no special chars)
            f.write(f'<option value="{genre}">{genre} ({cnt})</option>\n')

    # Print summary
    print(f"✅ Wrote normalized counts to `{OUTPUT_CSV}`")
    print(f"✅ Wrote HTML options to `{OUTPUT_OPTIONS}`")
