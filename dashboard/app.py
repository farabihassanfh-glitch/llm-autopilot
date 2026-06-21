import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

DB_PATH = Path(__file__).parent.parent / "logs" / "requests.db"

st.set_page_config(page_title="LLM Autopilot Dashboard", layout="wide")
st.title("LLM Autopilot — Request Dashboard")


@st.cache_data(ttl=5)
def load_data() -> pd.DataFrame:
    if not DB_PATH.exists():
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT * FROM requests ORDER BY id DESC", conn, parse_dates=["timestamp"]
    )
    conn.close()
    return df


df = load_data()

if df.empty:
    st.info("No requests logged yet. Send some prompts to get started.")
    st.stop()

# ── Top metrics ──────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Requests", len(df))
col2.metric("Total Cost", f"${df['cost_usd'].sum():.4f}")
col3.metric("Avg Latency", f"{df['latency_ms'].mean():.0f} ms")
col4.metric("Total Tokens Out", f"{df['output_tokens'].sum():,}")

st.divider()

# ── Charts ───────────────────────────────────────────────────────────────────
left, right = st.columns(2)

with left:
    st.subheader("Requests by Tier")
    tier_counts = df["complexity_tier"].value_counts().sort_index()
    tier_counts.index = [f"Tier {t}" for t in tier_counts.index]
    st.bar_chart(tier_counts)

with right:
    st.subheader("Cost by Model")
    cost_by_model = df.groupby("model_id")["cost_usd"].sum()
    st.bar_chart(cost_by_model)

left2, right2 = st.columns(2)

with left2:
    st.subheader("Avg Latency by Tier (ms)")
    latency_by_tier = df.groupby("complexity_tier")["latency_ms"].mean()
    latency_by_tier.index = [f"Tier {t}" for t in latency_by_tier.index]
    st.bar_chart(latency_by_tier)

with right2:
    st.subheader("Cumulative Cost Over Time")
    df_sorted = df.sort_values("timestamp")
    df_sorted["cumulative_cost"] = df_sorted["cost_usd"].cumsum()
    st.line_chart(df_sorted.set_index("timestamp")["cumulative_cost"])

st.divider()

# ── Raw table ────────────────────────────────────────────────────────────────
st.subheader("All Requests")
display_cols = ["id", "timestamp", "complexity_tier", "model_id",
                "input_tokens", "output_tokens", "cost_usd", "latency_ms"]
st.dataframe(df[display_cols], use_container_width=True)
