"""Fraud monitoring dashboard (Streamlit)."""
import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "db/fraud.db"

# Человекочитаемые названия правил (в коде они snake_case)
RULE_LABELS = {
    "large_amount": "Large amount",
    "orig_balance_zeroed": "Account drained",
    "high_dest_velocity": "High receiver velocity",
}

st.set_page_config(page_title="Fraud Monitoring", layout="wide")
st.title("Transaction Fraud Monitoring")

conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT * FROM decisions ORDER BY id DESC", conn)
conn.close()

# --- Top metrics ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total transactions", len(df))
c2.metric("Blocked", int((df["decision"] == "block").sum()))
c3.metric("Review", int((df["decision"] == "review").sum()))
c4.metric("Allowed", int((df["decision"] == "allow").sum()))

frauds = int((df["is_fraud"] == 1).sum())
caught = int(((df["is_fraud"] == 1) & (df["decision"] != "allow")).sum())
st.caption(f"Fraud in stream: {frauds}  ·  flagged (review or block): {caught}")

# --- Top fired rules ---
st.subheader("Top fired rules")
rules = df["fired_rules"].str.split(",").explode()
rules = rules[rules != ""]
if len(rules):
    counts = rules.value_counts()
    counts.index = counts.index.map(lambda r: RULE_LABELS.get(r, r))   # коды -> подписи
    st.bar_chart(counts)
else:
    st.write("No rules fired.")

# --- Decision stream ---
st.subheader("Decision stream (newest first)")

def friendly_rules(s):
    if not s:
        return ""
    return ", ".join(RULE_LABELS.get(r, r) for r in s.split(","))

view = df[["step", "amount", "name_dest", "fraud_prob", "fired_rules", "decision", "is_fraud"]].copy()
view["fired_rules"] = view["fired_rules"].apply(friendly_rules)
view = view.rename(columns={
    "step": "Step (hour)",
    "amount": "Amount",
    "name_dest": "Receiver",
    "fraud_prob": "ML score",
    "fired_rules": "Triggered rules",
    "decision": "Decision",
    "is_fraud": "Actually fraud",
})

def highlight(row):
    colour = {"block": "#ffd6d6", "review": "#fff2cc", "allow": ""}[row["Decision"]]
    return [f"background-color: {colour}"] * len(row)

styled = (view.style
          .apply(highlight, axis=1)
          .format({"Amount": "{:,.2f}", "ML score": "{:.3f}"}))
st.dataframe(styled, use_container_width=True)