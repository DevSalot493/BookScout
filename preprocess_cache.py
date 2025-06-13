import pandas as pd
from bs4 import BeautifulSoup
from wikipedia_fallback import get_wikipedia_plot

CACHE_FILE = "cache/book_data.csv"

# Fix: ensure non-string input doesn't break BeautifulSoup
def clean_description(desc):
    if not isinstance(desc, str):
        desc = ""
    return BeautifulSoup(desc, "html.parser").get_text().strip()

def preprocess_csv():
    df = pd.read_csv(CACHE_FILE)

    if "clean_description" not in df.columns:
        df["clean_description"] = ""

    for i, row in df.iterrows():
        raw = row.get("description", "")
        clean = clean_description(raw)

        # If still empty or weak, use Wikipedia
        if not clean or len(clean) < 30:
            print(f"📚 Falling back to Wikipedia for: {row['title']}")
            wiki_plot = get_wikipedia_plot(row["title"])
            if wiki_plot:
                clean = clean_description(wiki_plot)

        df.at[i, "clean_description"] = clean

    df.to_csv(CACHE_FILE, index=False)
    print("✅ Preprocessing complete. Updated CSV written.")

if __name__ == "__main__":
    preprocess_csv()
