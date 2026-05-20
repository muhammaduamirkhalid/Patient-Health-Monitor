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


