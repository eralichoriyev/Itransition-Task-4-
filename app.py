from pathlib import Path
import argparse

from core.io import load_orders, load_users, load_books_yaml
from core.metrics import compute_metrics

def process_folder(folder):
    folder = Path(folder)
    orders = load_orders(folder / "orders.parquet")
    users = load_users(folder / "users.csv")
    books = load_books_yaml(folder / "books.yaml")
    return compute_metrics(orders, users, books, folder.name)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("folders", nargs="+")
    args = parser.parse_args()
    for f in args.folders:
        print("Processing", f)
        process_folder(f)
        print("Done")

if __name__ == "__main__":
    main()
