from pathlib import Path
import pandas as pd
import yaml

def load_orders(path):
    p = Path(path)
    if p.suffix.lower() == '.csv':
        return pd.read_csv(p)
    return pd.read_parquet(p)

def load_users(path):
    return pd.read_csv(path)

def load_books_yaml(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    if isinstance(data, dict):
        items = []
        for k, v in data.items():
            if isinstance(v, dict):
                book = {'book_id': int(k) if str(k).isdigit() else k}
                book.update(v)
                items.append(book)
            else:
                items.append({'book_id': k, 'authors': v})
        return pd.DataFrame(items)
    if isinstance(data, list):
        return pd.DataFrame(data)
    return pd.DataFrame()
