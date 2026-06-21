import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

DB_PATH = Path(__file__).parent.parent / "logs" / "requests.db"

SONNET_PRICE_INPUT = 0.000003
SONNET_PRICE_OUTPUT = 0.000015

st.set_page_config(page_title="LLM Autopilot Dashboard", layout="wide")
st.title("LLM Autopilot Dashboard")

if not DB_PATH.exists():
    st.warning("No requests logged yet. Send some completions first.")
    st.stop()

con = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT * FROM requests ORDER BY timestamp DESC", con)
con.close()

if df.empty:
    st.warning("No requests logged yet.")
    st.stop()

df["cost_if_sonnet"] = (
    df["input_tokens"] * SONNET_PRICE_INPUT + df["output_tokens"] * SONNET_PRICE_OUTPUT
)

total_requests = len(df)
total_cost = df["cost_usd"].sum()
total_if_sonnet = df["cost_if_sonnet"].sum()
total_saved = total_if_sonnet - total_cost
savings_pct = (total_saved / total_if_sonnet * 100) if total_if_sonnet > 0 else 0.0

# ── Top metrics ──────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Requests", total_requests)
c2.metric("Total Actual Cost", f"${total_cost:.4f}")
c3.metric("Cost if All Sonnet", f"${total_if_sonnet:.4f}")
c4.metric("Total Saved", f"${total_saved:.4f}", delta=f"{savings_pct:.1f}% savings")

st.divider()

# ── Requests by model ────────────────────────────────────────────────────────
st.subheader("Requests by Model")
model_counts = df["model_id"].value_counts()
st.bar_chart(model_counts)

st.divider()

# ── Recent requests ──────────────────────────────────────────────────────────
st.subheader("Recent Requests")
st.dataframe(
    df[["timestamp", "prompt_hash", "complexity_tier", "model_id",
        "input_tokens", "output_tokens", "cost_usd", "latency_ms"]],
    use_container_width=True,
)
