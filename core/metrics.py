from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter, defaultdict

from .price import clean_price
from .timestamp import parse_timestamp
from .users import reconcile_users
from .books import compute_author_sets

def clean_orders_df(df):
    df = df.copy()
    df['unit_price_clean'] = df['unit_price'].apply(clean_price) if 'unit_price' in df.columns else None
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0).astype(int) if 'quantity' in df.columns else 1
    df['paid_price'] = df['quantity'] * df['unit_price_clean']
    df['timestamp_parsed'] = df['timestamp'].apply(parse_timestamp) if 'timestamp' in df.columns else pd.NaT
    df['date'] = df['timestamp_parsed'].dt.date
    df['date_str'] = df['timestamp_parsed'].dt.strftime('%Y-%m-%d')
    return df

def compute_metrics(orders_df, users_df, books_df, out_prefix):
    orders = clean_orders_df(orders_df)
    books_auth = compute_author_sets(books_df)
    merged = orders.merge(books_auth, how='left', left_on='book_id', right_on='book_id')
    users_clean = reconcile_users(users_df)
    merged = merged.merge(users_clean[['id','uid','real_user']], how='left', left_on='user_id', right_on='id')

    daily = merged.groupby('date_str', as_index=False)['paid_price'].sum().rename(columns={'paid_price':'daily_revenue'})
    daily_sorted = daily.sort_values('daily_revenue', ascending=False)
    top5 = daily_sorted.head(5).copy()
    top5['date_str'] = pd.to_datetime(top5['date_str'], errors='coerce').dt.strftime('%Y-%m-%d')

    num_real_users = users_clean['real_user'].nunique()
    num_author_sets = books_auth['author_set'].nunique()

    q_by_authorset = merged.groupby('author_set')['quantity'].sum().reset_index()
    q_by_authorset = q_by_authorset.sort_values('quantity', ascending=False)
    most_popular_sets = q_by_authorset[q_by_authorset['quantity'] == q_by_authorset['quantity'].max()]
    most_popular_authors = set()
    for s in most_popular_sets['author_set'].tolist():
        for a in s:
            most_popular_authors.add(a)

    counter = Counter()
    for authors, qty in zip(merged['author_set'], merged['quantity']):
        for a in authors:
            counter[a] += int(qty)
    if counter:
        top_qty = max(counter.values())
        top_authors = sorted([a for a,q in counter.items() if q == top_qty])
    else:
        top_authors = []

    spend_by_real = merged.groupby('real_user', as_index=False)['paid_price'].sum().sort_values('paid_price', ascending=False)
    best_buyers = []
    if not spend_by_real.empty:
        top_spend = spend_by_real['paid_price'].max()
        best_real_users = spend_by_real[spend_by_real['paid_price'] == top_spend]['real_user'].tolist()
        uid_map = defaultdict(list)
        for _, row in users_clean.iterrows():
            uid_map[row['real_user']].append(str(row['id']))
        for ru in best_real_users:
            best_buyers.append(uid_map.get(ru, []))

    output = {
        'top5_days': top5[['date_str','daily_revenue']].to_dict(orient='records'),
        'num_real_users': int(num_real_users),
        'num_author_sets': int(num_author_sets),
        'most_popular_authors': list(sorted(most_popular_authors)) if most_popular_authors else top_authors,
        'best_buyers_uid_arrays': best_buyers,
        'daily_revenue_series': daily.sort_values('date_str')[['date_str','daily_revenue']].to_dict(orient='records')
    }

    outdir = Path('outputs')
    outdir.mkdir(exist_ok=True)
    json_path = outdir / f"{out_prefix}_results.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    dr = pd.DataFrame(output['daily_revenue_series'])
    if not dr.empty:
        plt.figure(figsize=(10,5))
        plt.plot(dr['date_str'], dr['daily_revenue'])
        plt.xticks(rotation=45)
        plt.title(f"Daily revenue - {out_prefix}")
        plt.xlabel("Date")
        plt.ylabel("Revenue (USD)")
        plt.tight_layout()
        png_path = outdir / f"{out_prefix}_daily_revenue.png"
        plt.savefig(png_path)
        plt.close()
    return output
