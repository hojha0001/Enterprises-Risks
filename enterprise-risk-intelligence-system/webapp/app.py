import streamlit as st
import plotly.express as px
import pandas as pd
import requests
import json
from datetime import datetime, timedelta
import os
from requests.exceptions import RequestException
from pathlib import Path

st.set_page_config(
    page_title="ERIS Dashboard",
    page_icon="🎯",
    layout="wide"
)

st.title("Enterprise Risk Intelligence System")
# Configurable API URL (can be overridden with ERIS_API_URL env var)
API_URL = os.getenv("ERIS_API_URL", "http://localhost:8000")

# Simple navigation
PAGES = ["Dashboard", "Historical Risk Scores"]
selected_page = st.sidebar.selectbox("Page", PAGES)

# Optionally show a small link to the repository or docs
repo_url = os.getenv("ERIS_REPO_URL", "")
if repo_url:
    st.sidebar.markdown(f"[Repository]({repo_url})")


@st.cache_data(ttl=30)
def check_api_health(timeout: int = 3):
    """Check backend /health endpoint and return a small status dict.

    Cached for 30 seconds to avoid spamming the backend from the UI.
    """
    try:
        r = requests.get(f"{API_URL}/health", timeout=timeout)
        r.raise_for_status()
        data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        return {"ok": True, "status_code": r.status_code, "data": data}
    except RequestException as exc:
        return {"ok": False, "error": str(exc)}


def call_risk_score(payload: dict, timeout: int = 5):
    """POST to backend /risk/score and return parsed JSON or an error dict."""
    try:
        r = requests.post(f"{API_URL}/risk/score", json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except RequestException as exc:
        return {"error": str(exc)}


# API Health Check (display)
health = check_api_health()
if health.get("ok"):
    status_text = f"API Status: Healthy ✅ ({health.get('status_code')})"
    st.sidebar.success(status_text)
    if health.get("data"):
        # show version if provided by backend
        st.sidebar.info(f"API: {health['data'].get('version', '')}")
else:
    err = health.get("error", "Unavailable")
    st.sidebar.error(f"API Status: Unavailable ❌\n{err}")

if selected_page == "Dashboard":
    # Risk Score Demo
    st.header("Risk Score Calculator")

    with st.form("risk_calculator"):
        client_id = st.text_input("Client ID")
        
        col1, col2 = st.columns(2)
        with col1:
            financial_health = st.slider("Financial Health Score", 0, 100, 50)
            market_volatility = st.slider("Market Volatility", 0, 100, 30)
        with col2:
            compliance_score = st.slider("Compliance Score", 0, 100, 70)
            operational_risk = st.slider("Operational Risk", 0, 100, 40)
        
        submitted = st.form_submit_button("Calculate Risk Score")
        
        if submitted and client_id:
            risk_factors = {
                "financial_health": financial_health,
                "market_volatility": market_volatility,
                "compliance_score": compliance_score,
                "operational_risk": operational_risk
            }
            
            payload = {"client_id": client_id, "risk_factors": risk_factors}
            result = call_risk_score(payload)

            if isinstance(result, dict) and result.get("error"):
                st.error(f"Error calculating risk score: {result.get('error')}")
            else:
                response = result
                # Show score if present
                try:
                    st.success(f"Risk Score: {response['score']:.2f}")
                except Exception:
                    st.error("Invalid response from API: missing 'score'")

                # Radar Chart (use submitted risk_factors for visualization)
                df = pd.DataFrame({
                    'Factor': list(risk_factors.keys()),
                    'Value': list(risk_factors.values())
                })

                fig = px.line_polar(df, r='Value', theta='Factor', line_close=True)
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    showlegend=False
                )

                st.plotly_chart(fig)

elif selected_page == "Historical Risk Scores":
    st.header("Historical Risk Scores")
    # Load long-form description from a markdown file if present
    md_path = Path(__file__).with_name("historical.md")
    if md_path.exists():
        try:
            st.markdown(md_path.read_text(encoding="utf-8"))
        except Exception:
            st.info("Coming soon: Historical risk score tracking and trend analysis")
    else:
        st.info("Coming soon: Historical risk score tracking and trend analysis")
    # Placeholder area for future charts and filters
    st.write("")
    st.warning("This feature is not implemented yet. We'll add time-series charts, filters, and storage-backed history soon.")

    # Demo dataset (client-side) to preview the UI without backend history
    if st.checkbox("Show demo data", value=True):
        import random
        now = datetime.utcnow()
        dates = [now - timedelta(days=7 * i) for i in range(12)][::-1]
        clients = ["Demo Client A", "Demo Client B"]
        demo_rows = []
        for client_name in clients:
            base = 50 if client_name.endswith("A") else 40
            for d in dates:
                demo_rows.append({
                    "client_id": client_name,
                    "timestamp": d,
                    "score": max(0, min(100, base + random.uniform(-15, 15)))
                })

        df_demo = pd.DataFrame(demo_rows)
        df_demo['timestamp'] = pd.to_datetime(df_demo['timestamp'])

        chosen = st.selectbox("Choose demo client", options=clients)
        df_plot = df_demo[df_demo['client_id'] == chosen]
        fig = px.line(df_plot.sort_values('timestamp'), x='timestamp', y='score', markers=True, title=f"Historical risk scores — {chosen}")
        fig.update_yaxes(range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)