import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer
from scipy.sparse import hstack


def load_and_vectorize(csv_path='cache/book_data.csv'):
    df = pd.read_csv(csv_path)
    
    # Filter out empty or missing descriptions
    df = df[df['clean_description'].notnull() & (df['clean_description'].str.strip() != "")]
    df.reset_index(drop=True, inplace=True)

    # Clean and combine category data
    df['categories'] = df['categories'].fillna('')
    df['combined_text'] = df['clean_description'] + ' ' + df['categories'].str.lower()

    # TF-IDF on combined text (description + categories)
    tfidf = TfidfVectorizer(
        stop_words='english',
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.8
    )
    tfidf_matrix = tfidf.fit_transform(df['combined_text'])

    # One-hot encode genres/categories for structured signal
    cat_split = df['categories'].str.lower().str.split(', ')
    mlb = MultiLabelBinarizer()
    genre_matrix = mlb.fit_transform(cat_split)

    # Combine TF-IDF and genre matrix (genres weighted slightly less)
    combined_matrix = hstack([tfidf_matrix, genre_matrix * 0.5]).tocsr()

    return df, combined_matrix


def get_similar_books(title, filter_genres=None, top_n=5, csv_path='cache/book_data.csv'):
    """
    Returns top_n books most similar to `title`. 
    If filter_genres is provided (list of genre strings), only books matching at least one
    of those genres are considered in the similarity ranking.
    """
    # Load data and vector space
    df, combined_matrix = load_and_vectorize(csv_path)

    # Find the index of the query title
    matches = df.index[df['title'].str.lower() == title.lower()]
    if matches.empty:
        print(f"❌ Title '{title}' not found in cache.")
        return []
    idx = matches[0]

    # Compute cosine similarities
    sims = cosine_similarity(combined_matrix[idx], combined_matrix).flatten()

    # Sort indices by similarity desc, skip self
    sorted_indices = sims.argsort()[::-1]

    results = []
    count = 0
    for i in sorted_indices:
        if i == idx:
            continue

        # If filtering by genre, enforce at least one match
        if filter_genres:
            book_cats = [g.strip().lower() for g in df.at[i, 'categories'].split(',')]
            if not any(fg.lower() in book_cats for fg in filter_genres):
                continue

        # Append result
        results.append({
            'title': df.at[i, 'title'],
            'author': df.at[i, 'author'],
            'categories': df.at[i, 'categories'],
            'rating': df.at[i, 'rating'],
            'clean_description': df.at[i, 'clean_description'],
            'similarity': round(float(sims[i]), 2)
        })
        count += 1
        if count >= top_n:
            break

    return results
