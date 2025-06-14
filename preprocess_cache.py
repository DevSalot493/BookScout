import pandas as pd
from bs4 import BeautifulSoup
import re
import requests

CACHE_FILE = "cache/book_data.csv"
PLOT_IDS = ["Plot", "Plot_summary", "Summary", "Overview", "Synopsis"]

def get_wikipedia_plot(raw_title):
    """
    Fallback: search Wikipedia and extract the 'Plot' (or similar) section,
    preferring “(novel)” pages and filtering out radio/film/TV entries.
    """
    try:
        clean_title = raw_title.split("[")[0].strip()
        # 1. Search
        resp = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": clean_title,
                "utf8": 1
            }
        ).json()
        results = resp.get("query", {}).get("search", [])
        if not results:
            return None

        # 2. Rank candidates
        def score(r):
            t = r["title"].lower()
            s = 0
            if "(novel)" in t: s += 100
            if clean_title.lower() in t: s += 50
            if any(k in t for k in ["radio", "tv", "film", "series"]): s -= 100
            return s

        best = sorted(results, key=score, reverse=True)[0]
        page_title = best["title"]
        page_url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
        html = requests.get(page_url).text

        # 3. Parse HTML and find the first plot-related section
        soup = BeautifulSoup(html, "html.parser")
        header = None
        for pid in PLOT_IDS:
            header = soup.find(id=pid)
            if header:
                break
        if not header:
            return None

        # 4. Collect paragraphs until the next <h2>
        paras = []
        for tag in header.find_all_next():
            if tag.name == "h2":
                break
            if tag.name == "p":
                paras.append(tag.get_text().strip())

        text = "\n".join(paras).strip()
        return text if len(text) > 200 else None

    except Exception:
        return None

def clean_description(desc):
    """Strip HTML tags from a description string."""
    if not isinstance(desc, str):
        desc = ""
    return BeautifulSoup(desc, "html.parser").get_text().strip()

def clean_title_for_wiki(title):
    """Remove any [bracketed] text from the title."""
    return re.sub(r"\[.*?\]", "", title).strip()

def _process_row(row):
    """
    Clean or fallback a single DataFrame row.
    Returns the final clean_description text.
    """
    raw = row.get("description", "")
    clean = clean_description(raw)

    if not clean or len(clean) < 30:
        cleaned_title = clean_title_for_wiki(row["title"])
        print(f"📚 Falling back for: {row['title']} → {cleaned_title}")
        plot = get_wikipedia_plot(cleaned_title)
        if plot:
            clean = clean_description(plot)

    return clean

def preprocess_all():
    """Run fallback/clean on every row in the CSV."""
    df = pd.read_csv(CACHE_FILE)
    if "clean_description" not in df.columns:
        df["clean_description"] = ""
    for idx, row in df.iterrows():
        df.at[idx, "clean_description"] = _process_row(row)
    df.to_csv(CACHE_FILE, index=False)
    print("✅ Bulk preprocessing complete.")

def preprocess_last_row():
    """Run fallback/clean only on the latest row in the CSV."""
    df = pd.read_csv(CACHE_FILE)
    if "clean_description" not in df.columns:
        df["clean_description"] = ""
    last_idx = df.index[-1]
    row = df.loc[last_idx]
    df.at[last_idx, "clean_description"] = _process_row(row)
    df.to_csv(CACHE_FILE, index=False)
    print(f"✅ Preprocessed row {last_idx}: {row['title']}")

if __name__ == "__main__":
    # When invoked directly, do a full CSV pass
    preprocess_all()
