import streamlit as st
import pandas as pd
from supabase import create_client

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Patient Health Dashboard",
    layout="wide"
)

st.title("📊 Patient Health Dashboard")

# ==================================================
# SUPABASE CONNECTION
# ==================================================

SUPABASE_URL = "https://yvcbuzjryivboukwalyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl2Y2J1empyeWl2Ym91a3dhbHljIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkyMDYxNDAsImV4cCI6MjA5NDc4MjE0MH0.1R4XTQhzKUgkbDDLegKyjMLM-JVTk7ScSjvD16m3gWM"

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# ==================================================
# LOAD PATIENT READINGS
# ==================================================

response = supabase.table("patient_readings").select("*").execute()

data = response.data

df = pd.DataFrame(data)
st.subheader("Raw Data")
st.dataframe(df)
df = df.sort_values("created_at")

# Graph trends
st.subheader("Pulse Over Time")

st.line_chart(df.set_index("created_at")["pulse"])

st.subheader("Blood Pressure Over Time")

st.line_chart(
    df.set_index("created_at")[["systolic", "diastolic"]]
)
st.subheader("Oxygen Saturation (SpO2)")

st.line_chart(df.set_index("created_at")["spo2"])
# ==================================================
# SHOW DATA
# ==================================================

st.subheader("📄 Patient Readings")

st.dataframe(df)
# ==================================================
st.subheader("📊 Basic Health Summary")
# Add metrics
st.metric("Avg Pulse", round(df["pulse"].mean(), 1))
st.metric("Avg SpO2", round(df["spo2"].mean(), 1))
# Add blood Pressure Summary
st.metric("Avg Systolic", round(df["systolic"].mean(), 1))
st.metric("Avg Diastolic", round(df["diastolic"].mean(), 1))

# ==================================================
# Alerts
st.subheader("⚠️ Basic Alerts")
# Alert Rules
if df["pulse"].mean() > 100:
    st.error("High average pulse detected")

if df["spo2"].mean() < 94:
    st.warning("Low oxygen levels trend detected")

if df["systolic"].mean() > 140:
    st.error("High blood pressure trend detected")

# Code to detect real abnormal values not averages. 
st.subheader("⚠️ Real-Time Alerts")
# high pulse detection 
high_pulse = df[df["pulse"] > 120]

if not high_pulse.empty:
    st.error(f"High Pulse Events: {len(high_pulse)}")
# low oxygen concentration 
low_spo2 = df[df["spo2"] < 92]

if not low_spo2.empty:
    st.warning(f"Low SpO2 Events: {len(low_spo2)}")

# high blood pressure detection 
high_bp = df[(df["systolic"] > 140) | (df["diastolic"] > 90)]

if not high_bp.empty:
    st.error(f"High BP Events: {len(high_bp)}")
    
# Patient Health Score

def calculate_health_score(row):
    score = 100

    # Pulse penalty
    if row["pulse"] < 60 or row["pulse"] > 100:
        score -= 20

    # Blood pressure penalty
    if row["systolic"] > 140 or row["diastolic"] > 90:
        score -= 25

    # Oxygen penalty
    if row["spo2"] < 95:
        score -= 30

    return max(score, 0)

df["health_score"] = df.apply(calculate_health_score, axis=1)

# Latest patient score
st.subheader("🧠 Patient Health Score")

latest_score = df.iloc[-1]["health_score"]

st.metric("Current Health Score", int(latest_score))

# Visualize Score Trend
st.subheader("Health Score Trend")

st.line_chart(df.set_index("created_at")["health_score"])

# ===========Trend Intelligence Layer ==============

st.subheader("📈 Health Trend Analysis")

if len(df) > 5:

    recent = df["health_score"].tail(5).mean()
    previous = df["health_score"].head(5).mean()

    if recent > previous:
        st.success("📈 Patient condition is IMPROVING")
    elif recent < previous:
        st.error("📉 Patient condition is DETERIORATING")
    else:
        st.info("➖ Patient condition is STABLE")

# stabilty score
st.subheader("📊 Stability Index")

stability = 100 - abs(recent - previous)

st.metric("Stability Score", round(stability, 1))


