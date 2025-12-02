import json
from pathlib import Path
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

DATASETS = ["DATA1", "DATA2", "DATA3"]

def read_results(dataset):
    p = Path("outputs") / f"{dataset}_results.json"
    if not p.exists():
        return None
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

def render_dataset(dataset, results):
    st.header(dataset)
    if results is None:
        st.warning(f"No results file found for {dataset}. Run `python3 app.py {dataset}` first.")
        return

    st.subheader("Top 5 days by revenue")
    top5 = pd.DataFrame(results.get("top5_days", []))
    if not top5.empty:
        top5 = top5.rename(columns={"date_str":"date", "daily_revenue":"revenue"})
        top5["revenue"] = top5["revenue"].map(lambda v: f"${v:,.2f}")
        st.table(top5[["date","revenue"]].set_index("date"))
    else:
        st.write("No top5 data available.")

    cols = st.columns(3)
    cols[0].metric("Unique real users", results.get("num_real_users", "—"))
    cols[1].metric("Unique author sets", results.get("num_author_sets", "—"))
    mp = results.get("most_popular_authors", [])
    cols[2].write("Most popular author(s)")
    cols[2].write(mp if mp else "—")

    st.subheader("Best buyer (all alias user ids)")
    best_buyers = results.get("best_buyers_uid_arrays", [])
    if best_buyers:
        for idx, arr in enumerate(best_buyers, 1):
            st.write(f"{idx}. {arr}")
    else:
        st.write("No best buyer info found.")

    st.subheader("Daily revenue chart")
    dr = pd.DataFrame(results.get("daily_revenue_series", []))
    if dr.empty:
        st.write("No daily revenue series available.")
    else:
        dr = dr.copy()
        dr['date'] = pd.to_datetime(dr['date_str'], errors='coerce')
        dr = dr.sort_values('date')
        fig, ax = plt.subplots(figsize=(10,4))
        ax.plot(dr['date'], dr['daily_revenue'], marker='o', linewidth=1)
        ax.set_xlabel("Date")
        ax.set_ylabel("Revenue (USD)")
        ax.set_title(f"Daily revenue — {dataset}")
        ax.grid(True, linestyle='--', alpha=0.5)
        fig.autofmt_xdate()
        st.pyplot(fig)

def main():
    st.set_page_config(page_title="Book Sales Dashboard", layout="wide")
    st.title("Book Sales — Task 4 Dashboard")
    tabs = st.tabs(DATASETS)
    for tab_name, tab in zip(DATASETS, tabs):
        with tab:
            results = read_results(tab_name)
            render_dataset(tab_name, results)

if __name__ == "__main__":
    main()
