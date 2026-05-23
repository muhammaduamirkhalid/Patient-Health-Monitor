# ======================================================
# 📊 PATIENT HEALTH REPORT GENERATOR
# ======================================================

import os
import pandas as pd
import requests
from supabase import create_client

# ======================================================
# 🔐 STEP 1: LOAD SECRETS (FROM GITHUB ACTIONS)
# ======================================================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

# ======================================================
# 📧 STEP 2: EMAIL CONFIG (CHANGE THIS)
# 👉 PUT YOUR EMAIL HERE (receiver)
# ======================================================
TO_EMAIL = "pakistanijrl@gmail.com"   # <-- CHANGE THIS

# ======================================================
# 🔌 CONNECT TO SUPABASE
# ======================================================
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ======================================================
# 📥 LOAD PATIENT DATA
# ======================================================
def load_data():
    res = supabase.table("patient_readings").select("*").execute()
    df = pd.DataFrame(res.data)

    if df.empty:
        return df

    df["created_at"] = pd.to_datetime(df["created_at"])
    return df

# ======================================================
# 🧠 SIMPLE HEALTH SCORE (same logic as your dashboard)
# ======================================================
def calculate_score(row):
    score = 100

    if row["pulse"] < 60 or row["pulse"] > 100:
        score -= 20

    if row["systolic"] > 140 or row["diastolic"] > 90:
        score -= 25

    if row["spo2"] < 95:
        score -= 30

    return max(score, 0)

# ======================================================
# 📊 GENERATE REPORT TEXT
# ======================================================
def generate_report(df):

    if df.empty:
        return "No patient data available"

    df = df.sort_values("created_at")
    df["health_score"] = df.apply(calculate_score, axis=1)

    latest = df.iloc[-1]

    report = f"""
==============================
DAILY PATIENT HEALTH REPORT
==============================

Pulse: {latest['pulse']}
SpO2: {latest['spo2']}
Blood Pressure: {latest['systolic']}/{latest['diastolic']}

Health Score: {latest['health_score']}

==============================
Generated Automatically
"""

# services/email_builder.py

from datetime import datetime

# ---------------------------------------------------------
# 1. FETCH LATEST MEDICINE BASE (IMPORTANT NEW RULE)
# ---------------------------------------------------------
def get_latest_medicine_base(db_session):
    """
    Fetch latest entry from Medicine_base table.
    RULE: Always use latest record only.
    """

    query = """
    SELECT *
    FROM Medicine_base
    ORDER BY id DESC
    LIMIT 1
    """

    result = db_session.execute(query).fetchone()
    return result


# ---------------------------------------------------------
# 2. BUILD EMAIL HTML
# ---------------------------------------------------------
def build_health_email(patient, vitals, medicine_impact, medicine_base):

    now = datetime.now().strftime("%B %d, %Y")

    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f5f7fb;
                margin: 0;
                padding: 0;
            }}
            .container {{
                width: 100%;
                max-width: 900px;
                margin: auto;
                background: white;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(90deg, #0b3d91, #1e88e5);
                color: white;
                padding: 20px;
                border-radius: 10px;
            }}
            .section {{
                margin-top: 20px;
                padding: 15px;
                border-radius: 10px;
                background: #ffffff;
                border: 1px solid #e0e0e0;
            }}
            .title {{
                font-size: 18px;
                font-weight: bold;
                color: #0b3d91;
                margin-bottom: 10px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
            }}
            th {{
                background-color: #0b3d91;
                color: white;
            }}
            .good {{
                color: green;
                font-weight: bold;
            }}
        </style>
    </head>

    <body>
    <div class="container">

        <!-- HEADER -->
        <div class="header">
            <h2>Health Monitor - Daily Health Report</h2>
            <p>{now}</p>
        </div>

        <!-- GREETING SECTION -->
        <div class="section">
            <p><b>Hello {patient['name']},</b></p>
            <p>Your overall health status is: <span class="good">Good</span></p>
        </div>

        <!-- VITALS SECTION -->
        <div class="section">
            <div class="title">Today's Vitals Summary</div>
            <table>
                <tr>
                    <th>Heart Rate</th>
                    <th>BP</th>
                    <th>Glucose</th>
                    <th>SpO2</th>
                    <th>Temp</th>
                </tr>
                <tr>
                    <td>{vitals['heart_rate']} bpm</td>
                    <td>{vitals['bp']}</td>
                    <td>{vitals['glucose']} mg/dL</td>
                    <td>{vitals['spo2']}%</td>
                    <td>{vitals['temp']} °F</td>
                </tr>
            </table>
        </div>

        <!-- MEDICINE IMPACT -->
        <div class="section">
            <div class="title">Medicine Impact Summary</div>
            <table>
                <tr>
                    <th>Name</th>
                    <th>Purpose</th>
                    <th>Impact</th>
                    <th>Status</th>
                </tr>
                {medicine_impact}
            </table>
        </div>

        <!-- NEW: MEDICINE BASE (LATEST ENTRY ONLY) -->
        <div class="section">
            <div class="title">Medicine Base (Active Configuration)</div>
            <table>
                <tr>
                    <th>Base Name</th>
                    <th>Content</th>
                    <th>Updated At</th>
                </tr>
                <tr>
                    <td>{medicine_base['base_name']}</td>
                    <td>{medicine_base['content']}</td>
                    <td>{medicine_base['updated_at']}</td>
                </tr>
            </table>
        </div>

        <!-- FOOTER -->
        <div class="section">
            <p><b>Tip of the Day:</b> Stay consistent with medication and hydration.</p>
            <p>This is an automated report. Please do not reply.</p>
        </div>

    </div>
    </body>
    </html>
    """

    return html
    return report
    
    from services.email_builder import build_health_email, get_latest_medicine_base
    medicine_base = get_latest_medicine_base(db_session)


# ======================================================
# 📧 SEND EMAIL USING RESEND API
# ======================================================
def send_email(report_text):

    url = "https://api.resend.com/emails"

    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "from": "Health Monitor <onboarding@resend.dev>",
        "to": [TO_EMAIL],
        "subject": "📊 Daily Patient Health Report",
        "text": report_text
    }

    response = requests.post(url, json=data, headers=headers)

    print("Email Status:", response.status_code)
    print("Response:", response.text)

# ======================================================
# 🚀 MAIN EXECUTION
# ======================================================
if __name__ == "__main__":

    df = load_data()
    report = generate_report(df)

    print(report)
    send_email(report)
