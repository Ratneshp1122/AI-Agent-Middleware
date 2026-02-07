import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
import plotly.graph_objects as go
import time


st.set_page_config(page_title="AI Monitor", layout="wide")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "..", "logs", "audit.jsonl")

def load_data():
    """
    Robust data loading function.
    Returns: DataFrame (empty if no logs)
    """
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame()

    data = []
    try:
        with open(LOG_FILE, "r", encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        st.error(f"Error reading DB: {e}")
        return pd.DataFrame()
    
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    

    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        
    return df

st.title("AI Security Middleware")
st.markdown("Real-time monitoring of AI Agent traffic.")

if st.sidebar.checkbox("Auto-refresh (5s)", value=True):
    time.sleep(5)
    st.rerun()

df = load_data()

if df.empty:
    st.info("Waiting for traffic... No logs recorded yet.")
    st.stop()

total = len(df)
blocked = len(df[df['decision'] == 'BLOCK'])
allowed = len(df[df['decision'] == 'ALLOW'])
block_rate = (blocked / total * 100) if total > 0 else 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Requests", total)
m2.metric("Shield Blocked", blocked, delta_color="inverse")
m3.metric("Allowed", allowed)
m4.metric("Block Rate", f"{block_rate:.1f}%")

st.markdown("---")

c1, c2 = st.columns(2)

with c1:
    st.subheader("Traffic Distribution")
    try:
        decision_counts = df['decision'].value_counts().reset_index()
        decision_counts.columns = ['Decision', 'Count']
        
        fig = px.pie(
            decision_counts, 
            values='Count', 
            names='Decision',
            color='Decision',
            color_discrete_map={'BLOCK': 'red', 'ALLOW': 'green'},
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Chart Error: {e}")

with c2:
    st.subheader("Requests Timeline")
    try:
        if 'timestamp' in df.columns and not df.empty:
            
            df_time = df.set_index('timestamp').resample('10s')['decision'].count().reset_index()
            df_time.columns = ['Time', 'Requests']
            
            fig2 = px.line(df_time, x='Time', y='Requests', title="Requests per 10s")
            st.plotly_chart(fig2, use_container_width=True)
    except Exception as e:
        st.error(f"Timeline Error: {e}")
st.subheader("Traffic Inspector")

filter_type = st.selectbox("Status Filter", ["All", "BLOCK", "ALLOW"])

view_df = df.copy()
if filter_type != "All":
    view_df = view_df[view_df['decision'] == filter_type]

st.dataframe(
    view_df.sort_values('timestamp', ascending=False),
    use_container_width=True,
    column_config={
        "timestamp": st.column_config.DatetimeColumn("Time", format="D MMM, HH:mm:ss"),
        "url": "URL",
        "method": "Method",
        "decision": st.column_config.TextColumn("Decision"),
        "metadata": "Details"
    }
)
