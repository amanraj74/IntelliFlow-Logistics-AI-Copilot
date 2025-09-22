import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# Configuration
API_BASE = st.secrets.get("API_BASE", "http://localhost:8000")
TIMEOUT = 10

st.set_page_config(
    page_title="IntelliFlow Logistics AI", 
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #e0e0e0;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .alert-high {
        background-color: #ffebee;
        color: #c62828;
        padding: 0.5rem;
        border-radius: 0.25rem;
        border-left: 4px solid #f44336;
    }
    .alert-medium {
        background-color: #fff3e0;
        color: #ef6c00;
        padding: 0.5rem;
        border-radius: 0.25rem;
        border-left: 4px solid #ff9800;
    }
    .status-ok {
        color: #4caf50;
        font-weight: bold;
    }
    .status-error {
        color: #f44336;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🚛 IntelliFlow Logistics AI Dashboard</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🔧 System Controls")
    
    # Auto-refresh toggle
    auto_refresh = st.checkbox("Auto Refresh (30s)", value=False)
    
    # Manual refresh button
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.rerun()
    
    st.divider()
    
    # System status check
    st.subheader("📊 System Status")
    
    try:
        health_response = requests.get(f"{API_BASE}/health", timeout=5)
        if health_response.status_code == 200:
            st.markdown('<p class="status-ok">✅ API Online</p>', unsafe_allow_html=True)
            api_status = True
        else:
            st.markdown('<p class="status-error">❌ API Issues</p>', unsafe_allow_html=True)
            api_status = False
    except Exception as e:
        st.markdown('<p class="status-error">❌ API Offline</p>', unsafe_allow_html=True)
        st.error(f"Connection error: {str(e)[:50]}...")
        api_status = False

# Main content
if not api_status:
    st.error("⚠️ Backend API is not available. Please start the backend service.")
    st.code("python -m backend.api.main")
    st.stop()

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["🤖 AI Copilot", "👥 Drivers", "📋 Incidents", "🚨 Alerts"])

with tab1:
    st.header("AI Logistics Copilot")
    st.write("Ask questions about drivers, incidents, safety, and logistics operations.")
    
    # Chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        question = st.text_input(
            "Ask a question:",
            placeholder="Which drivers are high-risk today?",
            key="ai_question"
        )
    
    with col2:
        ask_button = st.button("🤖 Ask AI", use_container_width=True)
    
    # Example questions
    st.write("**💡 Try these questions:**")
    example_questions = [
        "Which drivers are high-risk today?",
        "Show me recent incidents",
        "What alerts are active?",
        "Driver safety summary"
    ]
    
    example_cols = st.columns(len(example_questions))
    for i, eq in enumerate(example_questions):
        with example_cols[i]:
            if st.button(eq, key=f"example_{i}", use_container_width=True):
                question = eq
                ask_button = True
    
    if (ask_button and question) or question in example_questions:
        with st.spinner("🔍 AI is thinking..."):
            try:
                ai_response = requests.post(
                    f"{API_BASE}/ai/query",
                    json={"question": question},
                    timeout=TIMEOUT
                )
                
                if ai_response.status_code == 200:
                    result = ai_response.json()
                    
                    # Display answer
                    st.success("**🤖 AI Response:**")
                    st.write(result.get("answer", "No answer provided"))
                    
                    # Show confidence and sources
                    col1, col2 = st.columns(2)
                    with col1:
                        confidence = result.get("confidence", 0)
                        st.metric("Confidence", f"{confidence:.1%}")
                    
                    with col2:
                        sources = result.get("sources", [])
                        st.write(f"**Sources:** {', '.join(sources)}")
                
                else:
                    st.error(f"AI Error: {ai_response.status_code}")
                    
            except Exception as e:
                st.error(f"Failed to get AI response: {str(e)}")

with tab2:
    st.header("Driver Management")
    
    try:
        drivers_response = requests.get(f"{API_BASE}/drivers/", timeout=TIMEOUT)
        if drivers_response.status_code == 200:
            drivers_data = drivers_response.json()
            
            if drivers_data:
                df = pd.DataFrame(drivers_data)
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Drivers", len(df))
                with col2:
                    high_risk = len(df[df['risk_score'] > 0.7])
                    st.metric("High Risk", high_risk, delta=f"{high_risk/len(df)*100:.1f}%")
                with col3:
                    avg_risk = df['risk_score'].mean()
                    st.metric("Avg Risk Score", f"{avg_risk:.2f}")
                with col4:
                    max_risk_driver = df.loc[df['risk_score'].idxmax()]
                    st.metric("Highest Risk", max_risk_driver['name'])
                
                # Driver table
                st.subheader("Driver List")
                
                # Add risk status column
                df['Risk Status'] = df['risk_score'].apply(
                    lambda x: '🔴 High' if x > 0.7 else '🟡 Medium' if x > 0.3 else '🟢 Low'
                )
                
                st.dataframe(
                    df[['name', 'license_number', 'risk_score', 'Risk Status']].rename(columns={
                        'name': 'Name',
                        'license_number': 'License',
                        'risk_score': 'Risk Score'
                    }),
                    use_container_width=True
                )
                
                # Risk distribution chart
                st.subheader("Risk Score Distribution")
                risk_bins = pd.cut(df['risk_score'], bins=[0, 0.3, 0.7, 1.0], labels=['Low', 'Medium', 'High'])
                risk_counts = risk_bins.value_counts()
                st.bar_chart(risk_counts)
                
            else:
                st.info("No drivers found")
        else:
            st.error("Failed to load drivers")
    except Exception as e:
        st.error(f"Error loading drivers: {str(e)}")

with tab3:
    st.header("Incident Reports")
    
    try:
        incidents_response = requests.get(f"{API_BASE}/incidents/", timeout=TIMEOUT)
        if incidents_response.status_code == 200:
            incidents_data = incidents_response.json()
            
            if incidents_data:
                df = pd.DataFrame(incidents_data)
                
                # Metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Incidents", len(df))
                with col2:
                    high_severity = len(df[df['severity'] == 'high'])
                    st.metric("High Severity", high_severity)
                with col3:
                    recent_incidents = len(df)  # All incidents are "recent" in demo
                    st.metric("Recent (7 days)", recent_incidents)
                
                # Incidents table
                st.subheader("Recent Incidents")
                
                # Add severity indicators
                severity_colors = {
                    'high': '🔴',
                    'medium': '🟡',
                    'low': '🟢'
                }
                
                df['Severity'] = df['severity'].apply(
                    lambda x: f"{severity_colors.get(x, '⚪')} {x.title()}"
                )
                
                st.dataframe(
                    df[['driver_id', 'date', 'Severity', 'description']].rename(columns={
                        'driver_id': 'Driver ID',
                        'date': 'Date',
                        'description': 'Description'
                    }),
                    use_container_width=True
                )
                
                # Severity distribution
                st.subheader("Severity Distribution")
                severity_counts = df['severity'].value_counts()
                st.bar_chart(severity_counts)
                
            else:
                st.info("No incidents found")
        else:
            st.error("Failed to load incidents")
    except Exception as e:
        st.error(f"Error loading incidents: {str(e)}")

with tab4:
    st.header("Active Alerts")
    
    try:
        alerts_response = requests.get(f"{API_BASE}/alerts/", timeout=TIMEOUT)
        if alerts_response.status_code == 200:
            alerts_data = alerts_response.json()
            
            if alerts_data:
                st.subheader(f"🚨 {len(alerts_data)} Active Alert(s)")
                
                for alert in alerts_data:
                    alert_type = alert.get('type', 'info')
                    priority = alert.get('priority', 'medium')
                    message = alert.get('message', 'No message')
                    
                    if priority == 'high':
                        st.markdown(
                            f'<div class="alert-high">🚨 <strong>HIGH PRIORITY:</strong> {message}</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f'<div class="alert-medium">⚠️ <strong>MEDIUM:</strong> {message}</div>',
                            unsafe_allow_html=True
                        )
            else:
                st.success("✅ No active alerts")
        else:
            st.error("Failed to load alerts")
    except Exception as e:
        st.error(f"Error loading alerts: {str(e)}")

# Auto-refresh functionality
if auto_refresh:
    time.sleep(30)
    st.rerun()

# Footer
st.divider()
st.markdown(
    "**IntelliFlow Logistics AI** | Real-time logistics intelligence powered by Pathway & AI",
    help="Built for Pathway X Iota Cluster IIT Ropar Gen AI Hackathon"
)