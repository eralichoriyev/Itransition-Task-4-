import re
import pandas as pd
from .price import normalize_string

def canonical_author_set(authors_field):
    if authors_field is None:
        return tuple()
    if isinstance(authors_field, list):
        parts = [normalize_string(x) for x in authors_field if x]
    else:
        parts = [normalize_string(x) for x in re.split(r';|,|/| and | & ', str(authors_field)) if x and normalize_string(x)]
    parts = sorted(set(parts))
    return tuple(parts)

def compute_author_sets(books_df):
    b = books_df.copy()
    if ':id' in b.columns:
        b = b.rename(columns={':id': 'book_id'})
    if ':author' in b.columns:
        b = b.rename(columns={':author': 'authors'})
    if 'book_id' in b.columns:
        b['book_id'] = b['book_id'].apply(lambda x: int(x) if pd.notna(x) else x)
    b['author_set'] = b['authors'].apply(canonical_author_set)
    return b[['book_id','author_set']]
