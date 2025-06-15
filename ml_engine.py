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

    # TF-IDF on combined text (desc + category terms)
    tfidf = TfidfVectorizer(
        stop_words='english',
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.8
    )
    tfidf_matrix = tfidf.fit_transform(df['combined_text'])

    # One-hot encode genres/categories
    cat_split = df['categories'].str.lower().str.split(', ')
    mlb = MultiLabelBinarizer()
    genre_matrix = mlb.fit_transform(cat_split)

    # Combine TF-IDF and genre matrix (genre weighted slightly less)
    combined_matrix = hstack([tfidf_matrix, genre_matrix * 0.5]).tocsr()

    return df, combined_matrix

def get_similar_books(title, top_n=5, csv_path='cache/book_data.csv'):
    df, combined_matrix = load_and_vectorize(csv_path)

    # Case-insensitive match from the reindexed dataframe
    idx_match = df[df['title'].str.lower() == title.lower()]
    if idx_match.empty:
        print(f"❌ Title '{title}' not found in cache.")
        return []

    idx = idx_match.index[0]  # This is now safe due to reset_index

    if idx >= combined_matrix.shape[0]:
        print(f"❌ Index {idx} is out of bounds for similarity matrix of shape {combined_matrix.shape}.")
        return []

    sims = cosine_similarity(combined_matrix[idx], combined_matrix).flatten()

    # Exclude self and get top-N
    top_indices = sims.argsort()[::-1][1:top_n + 1]
    similar_books = df.iloc[top_indices].copy()
    similar_books['similarity'] = sims[top_indices].round(2)

    return similar_books[['title', 'author', 'categories', 'rating', 'similarity']].to_dict(orient='records')
