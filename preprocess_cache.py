import pandas as pd
from bs4 import BeautifulSoup
import re
import requests
import time
from transformers import pipeline

CACHE_FILE = "cache/book_data.csv"
PLOT_IDS = ["Plot", "Plot_summary", "Summary", "Overview", "Synopsis"]
HEADERS = {"User-Agent": "BookScout/1.0 (contact: devsalot@gmail.com)"}

# ─── Zero‑Shot Classifier Setup ─────────────────────────────────────────────────
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
CANDIDATE_GENRES = [
    "Fantasy",
    "Science Fiction",
    "Horror",
    "Dystopian",
    "Adventure",
    "Classic",
    "Young Adult",
    "Historical Fiction",
    "Romance",
    "Coming-of-age",
    "Satire",
    "Thriller",
    "Mystery",
    "Philosophical Fiction",
    "Drama",
    "Self-help",
    "Non-fiction",
    "Memoir",
    # Broad buckets for any stragglers:
    "Fiction",
    "Non-Fiction",
    "Biography",
    "Literary Fiction",
    "Young-Adult Novel"
]


def clean_description(desc):
    if not isinstance(desc, str):
        desc = ""
    return BeautifulSoup(desc, "html.parser").get_text().strip()

def clean_title_for_wiki(title):
    return re.sub(r"\[.*?\]", "", title).strip()

def remove_footnotes(text):
    return re.sub(r"\[\d+\]", "", text)

def classify_genre_with_nli(description, top_n=2):
    """Zero‑shot fallback: infer top genres from description."""
    if not description or len(description) < 30:
        return ""
    result = classifier(description, CANDIDATE_GENRES, multi_label=True)
    genres = [lbl for lbl, sc in zip(result["labels"], result["scores"]) if sc > 0.4]
    return ", ".join(genres[:top_n]) if genres else ""

def get_wikipedia_plot(raw_title):
    try:
        clean_title = raw_title.split("[")[0].strip()
        resp = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action":"query","format":"json","list":"search","srsearch":clean_title,"utf8":1},
            headers=HEADERS,timeout=5
        ).json()
        results = resp.get("query",{}).get("search",[])
        if not results:
            return None, None

        def score(r):
            t = r["title"].lower(); s=0
            if "(novel)" in t: s+=100
            if clean_title.lower() in t: s+=50
            if any(k in t for k in ["radio","tv","film","series"]): s-=100
            return s

        best = sorted(results,key=score,reverse=True)[0]
        page_title = best["title"]
        html = requests.get(f"https://en.wikipedia.org/wiki/{page_title.replace(' ','_')}",headers=HEADERS).text
        soup = BeautifulSoup(html,"html.parser")
        header=None
        for pid in PLOT_IDS:
            header=soup.find(id=pid)
            if header: break
        if not header: return None, page_title

        paras=[]
        for tag in header.find_all_next():
            if tag.name=="h2": break
            if tag.name=="p": paras.append(tag.get_text().strip())
        text="\n".join(paras).strip()
        return (text if len(text)>200 else None), page_title

    except Exception:
        return None, None

def extract_wikipedia_categories(page_title):
    try:
        html = requests.get(
            f"https://en.wikipedia.org/wiki/{page_title.replace(' ','_')}",
            headers=HEADERS,timeout=5
        ).text
        soup = BeautifulSoup(html,"html.parser")
        infobox = soup.find("table",class_=re.compile(r"infobox"))
        if infobox:
            for row in infobox.find_all("tr"):
                th=row.find("th")
                if th and "genre" in th.get_text(strip=True).lower():
                    td=row.find("td")
                    if td:
                        for sup in td.find_all("sup"): sup.decompose()
                        raw=td.get_text(separator=", ")
                        return remove_footnotes(raw).strip()
        return ""
    except Exception as e:
        print(f"📚 Error extracting categories for '{page_title}':",e)
        return ""

def normalize_categories(cat_str):
    """
    Map each comma‑separated label to the first candidate genre
    whose name appears as a substring (case‑insensitive).
    Drop any labels that don't match.
    Deduplicate preserving order.
    """
    parts = [c.strip() for c in cat_str.split(",")]
    mapped = []
    for p in parts:
        for cand in CANDIDATE_GENRES:
            if cand.lower() in p.lower():
                mapped.append(cand)
                break
    # dedupe
    seen=set(); out=[]
    for m in mapped:
        if m not in seen:
            seen.add(m); out.append(m)
    return ", ".join(out)

def _process_row(row):
    raw=row.get("description","")
    clean=clean_description(raw)
    use_wiki = not clean or len(clean)<30

    cleaned_title=clean_title_for_wiki(row["title"])
    print(f"📚 Falling back for: {row['title']} → {cleaned_title}")
    plot,page_title=get_wikipedia_plot(cleaned_title)

    if plot and use_wiki:
        clean=clean_description(plot)
    row["clean_description"]=clean

    wiki_genres = extract_wikipedia_categories(page_title) if page_title else ""
    raw_cats = wiki_genres if wiki_genres else classify_genre_with_nli(clean)
    row["categories"] = normalize_categories(raw_cats)

    return row

def preprocess_all():
    df=pd.read_csv(CACHE_FILE)
    if "clean_description" not in df.columns: df["clean_description"]=""
    if "categories" not in df.columns: df["categories"]=""

    for idx,row in df.iterrows():
        print(f"🔄 Processing row {idx+1}/{len(df)}: {row['title']}")
        df.iloc[idx]=_process_row(row.copy()); time.sleep(1)

    df.to_csv(CACHE_FILE,index=False)
    print("✅ Bulk preprocessing complete.")

def preprocess_last_row():
    df=pd.read_csv(CACHE_FILE)
    if "clean_description" not in df.columns: df["clean_description"]=""
    if "categories" not in df.columns: df["categories"]=""

    last_idx=df.index[-1]
    print(f"🔄 Preprocessing new book: {df.loc[last_idx,'title']}")
    df.iloc[last_idx]=_process_row(df.loc[last_idx].copy())
    df.to_csv(CACHE_FILE,index=False)
    print(f"✅ Preprocessed row {last_idx}: {df.loc[last_idx,'title']}")

if __name__=="__main__":
    preprocess_all()
