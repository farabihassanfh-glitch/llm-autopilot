import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

DB_PATH = Path(__file__).parent.parent / "logs" / "requests.db"

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

# ── Cost savings ────────────────────────────────────────────────────────────
GPT4O_PRICE_INPUT = 0.000005
GPT4O_PRICE_OUTPUT = 0.000015

df["cost_if_gpt4o"] = (
    df["input_tokens"] * GPT4O_PRICE_INPUT + df["output_tokens"] * GPT4O_PRICE_OUTPUT
)
df["cost_saved"] = df["cost_if_gpt4o"] - df["cost_usd"]

total_cost = df["cost_usd"].sum()
total_if_gpt4o = df["cost_if_gpt4o"].sum()
total_saved = df["cost_saved"].sum()
total_requests = len(df)

# ── Top metrics ─────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Requests", total_requests)
c2.metric("Total Cost", f"${total_cost:.4f}")
c3.metric("Cost if All GPT-4o", f"${total_if_gpt4o:.4f}")
c4.metric("Total Saved", f"${total_saved:.4f}")

st.divider()

# ── Requests by tier ─────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Requests by Tier")
    tier_counts = df["complexity_tier"].value_counts().sort_index()
    tier_counts.index = [f"Tier {t}" for t in tier_counts.index]
    st.bar_chart(tier_counts)

with col2:
    st.subheader("Requests by Model")
    model_counts = df["model_id"].value_counts()
    st.bar_chart(model_counts)

st.divider()

# ── Cost over time ───────────────────────────────────────────────────────────
st.subheader("Cost per Request Over Time")
df["timestamp"] = pd.to_datetime(df["timestamp"])
cost_over_time = df.set_index("timestamp")[["cost_usd", "cost_if_gpt4o"]].sort_index()
cost_over_time.columns = ["Actual Cost", "Cost if GPT-4o"]
st.line_chart(cost_over_time)

st.divider()

# ── Latency by model ─────────────────────────────────────────────────────────
st.subheader("Avg Latency by Model (ms)")
avg_latency = df.groupby("model_id")["latency_ms"].mean().sort_values()
st.bar_chart(avg_latency)

st.divider()

# ── Raw logs ─────────────────────────────────────────────────────────────────
st.subheader("Recent Requests")
st.dataframe(
    df[["timestamp", "prompt_hash", "complexity_tier", "model_id",
        "input_tokens", "output_tokens", "cost_usd", "latency_ms"]]
    .head(50),
    use_container_width=True,
)
