import streamlit as st
import requests

API_BASE = st.secrets.get("API_BASE", "http://localhost:8000")


st.set_page_config(page_title="IntelliFlow Logistics AI", layout="wide")
st.title("IntelliFlow Logistics AI Dashboard")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Health Check"):
        try:
            resp = requests.get(f"{API_BASE}/health", timeout=5)
            st.success(resp.json())
        except Exception as e:
            st.error(str(e))

with col2:
    if st.button("List Drivers"):
        try:
            resp = requests.get(f"{API_BASE}/drivers/", timeout=5)
            st.json(resp.json())
        except Exception as e:
            st.error(str(e))

with col3:
    if st.button("List Alerts"):
        try:
            resp = requests.get(f"{API_BASE}/alerts/", timeout=5)
            st.json(resp.json())
        except Exception as e:
            st.error(str(e))

st.subheader("Ask the AI Copilot")
question = st.text_input("Question", placeholder="Which drivers are high-risk today?")
if st.button("Ask") and question:
    try:
        resp = requests.post(f"{API_BASE}/ai/query", json={"question": question}, timeout=10)
        st.write(resp.json().get("answer"))
        st.caption(f"Sources: {', '.join(resp.json().get('sources', []))}")
    except Exception as e:
        st.error(str(e))


