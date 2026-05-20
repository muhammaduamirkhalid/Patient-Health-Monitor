# ======================================================
# 📄 PATIENT DAILY REPORT GENERATOR (STANDALONE)
# ======================================================

import datetime
import pandas as pd
from supabase import create_client

# -------------------------------
# SUPABASE CONNECTION
# -------------------------------
SUPABASE_URL = "https://yvcbuzjryivboukwalyc.supabase.co"
SUPABASE_KEY = "YOUR_ANON_KEY"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------------
# LOAD DATA
# -------------------------------
def load_data():
    res = supabase.table("patient_readings").select("*").execute()
    df = pd.DataFrame(res.data)
    df["created_at"] = pd.to_datetime(df["created_at"])
    return df

# -------------------------------
# HEALTH SCORE (same logic you used)
# -------------------------------
def calculate_score(row):
    score = 100

    if row["pulse"] < 60 or row["pulse"] > 100:
        score -= 20

    if row["systolic"] > 140 or row["diastolic"] > 90:
        score -= 25

    if row["spo2"] < 95:
        score -= 30

    return max(score, 0)

# -------------------------------
# GENERATE REPORT
# -------------------------------
def generate_report():

    df = load_data()

    if df.empty:
        return "No data available"

    df = df.sort_values("created_at")
    df["health_score"] = df.apply(calculate_score, axis=1)

    latest = df.iloc[-1]

    report = f"""
========================
DAILY PATIENT REPORT
========================
Date: {datetime.datetime.now()}

Pulse: {latest['pulse']}
SpO2: {latest['spo2']}
BP: {latest['systolic']}/{latest['diastolic']}

Health Score: {latest['health_score']}

========================
"""

    return report

# -------------------------------
# TEST RUN
# -------------------------------
if __name__ == "__main__":
    print(generate_report())
