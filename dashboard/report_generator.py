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
# 📧 STEP 2: EMAIL CONFIG
# ======================================================
TO_EMAIL = "pakistanijrl@gmail.com"

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
# 🧠 SIMPLE HEALTH SCORE
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

def generate_html_report(df):

    if df.empty:
        return "<h1>No patient data available</h1>"

    # =========================================
    # SORT DATA
    # =========================================
    df = df.sort_values("created_at")

    # =========================================
    # HEALTH SCORE
    # =========================================
    df["health_score"] = df.apply(calculate_score, axis=1)

    latest = df.iloc[-1]

    # =========================================
    # CURRENT MEDICINE BASE
    # =========================================
    current_base = latest["medicine_base"]

    med_res = (
        supabase
        .table("medicine_bases")
        .select("*")
        .eq("base_name", current_base)
        .execute()
    )

    medicines_text = "No medicines found"

    if med_res.data:
        medicines_text = med_res.data[0]["medicines"]

    # =========================================
    # MEDICINE TABLE ROWS
    # =========================================
    medicine_rows = ""

    for med in medicines_text.split(","):

        medicine_rows += f"""
        <tr>
            <td style="
                padding:12px;
                border-bottom:1px solid #e5e7eb;
                font-size:14px;
            ">
                {med.strip()}
            </td>
        </tr>
        """

    # =========================================
    # HEALTH STATUS
    # =========================================
    health_score = latest["health_score"]

    if health_score >= 80:
        status_color = "#16a34a"
        status_text = "STABLE"

    elif health_score >= 60:
        status_color = "#f59e0b"
        status_text = "WARNING"

    else:
        status_color = "#dc2626"
        status_text = "CRITICAL"

    # =========================================
    # SIMPLE TREND SUMMARY
    # =========================================
    trend_summary = f"""
    Patient vitals were monitored successfully.
    Current health score indicates {status_text.lower()} condition.
    Continue observing pulse and blood pressure trends regularly.
    """

    # =========================================
    # HTML EMAIL TEMPLATE
    # =========================================
    html = f"""

    <html>

    <body style="
        margin:0;
        padding:30px;
        background:#eef2ff;
        font-family:Arial,sans-serif;
    ">

    <div style="
        max-width:820px;
        margin:auto;
        background:white;
        border-radius:20px;
        overflow:hidden;
        box-shadow:0 10px 30px rgba(0,0,0,0.08);
    ">

        <!-- HEADER -->
        <div style="
            background:linear-gradient(135deg,#2563eb,#1d4ed8);
            padding:35px;
            color:white;
            text-align:center;
        ">

            <h1 style="
                margin:0;
                font-size:32px;
            ">
                Patient Health Monitor
            </h1>

            <p style="
                margin-top:10px;
                opacity:0.9;
                font-size:15px;
            ">
                Daily Automated Health Report
            </p>

        </div>

        <!-- BODY -->
        <div style="padding:30px;">

            <!-- STATUS -->
            <div style="
                background:{status_color};
                color:white;
                padding:18px;
                border-radius:14px;
                text-align:center;
                font-size:24px;
                font-weight:bold;
                margin-bottom:28px;
            ">
                HEALTH STATUS: {status_text}
            </div>

            <!-- CARDS -->
            <table width="100%" cellspacing="12">

                <tr>

                    <td style="
                        background:#f8fafc;
                        padding:22px;
                        border-radius:16px;
                        text-align:center;
                        width:25%;
                    ">

                        <div style="
                            font-size:13px;
                            color:#6b7280;
                        ">
                            Pulse
                        </div>

                        <div style="
                            margin-top:8px;
                            font-size:28px;
                            font-weight:bold;
                            color:#111827;
                        ">
                            {latest['pulse']}
                        </div>

                        <div style="
                            color:#6b7280;
                            font-size:12px;
                        ">
                            BPM
                        </div>

                    </td>

                    <td style="
                        background:#f8fafc;
                        padding:22px;
                        border-radius:16px;
                        text-align:center;
                        width:25%;
                    ">

                        <div style="
                            font-size:13px;
                            color:#6b7280;
                        ">
                            Blood Pressure
                        </div>

                        <div style="
                            margin-top:8px;
                            font-size:24px;
                            font-weight:bold;
                            color:#111827;
                        ">
                            {latest['systolic']}/{latest['diastolic']}
                        </div>

                    </td>

                    <td style="
                        background:#f8fafc;
                        padding:22px;
                        border-radius:16px;
                        text-align:center;
                        width:25%;
                    ">

                        <div style="
                            font-size:13px;
                            color:#6b7280;
                        ">
                            SpO2
                        </div>

                        <div style="
                            margin-top:8px;
                            font-size:28px;
                            font-weight:bold;
                            color:#111827;
                        ">
                            {latest['spo2']}%
                        </div>

                    </td>

                    <td style="
                        background:#eff6ff;
                        padding:22px;
                        border-radius:16px;
                        text-align:center;
                        width:25%;
                    ">

                        <div style="
                            font-size:13px;
                            color:#2563eb;
                        ">
                            Health Score
                        </div>

                        <div style="
                            margin-top:8px;
                            font-size:30px;
                            font-weight:bold;
                            color:#2563eb;
                        ">
                            {health_score}
                        </div>

                        <div style="
                            font-size:12px;
                            color:#2563eb;
                        ">
                            /100
                        </div>

                    </td>

                </tr>

            </table>

            <!-- TREND SUMMARY -->
            <div style="
                margin-top:35px;
                background:#f9fafb;
                border-radius:16px;
                padding:24px;
            ">

                <h2 style="
                    margin-top:0;
                    color:#2563eb;
                ">
                    Health Trend Analysis
                </h2>

                <p style="
                    color:#374151;
                    line-height:1.8;
                    font-size:15px;
                ">
                    {trend_summary}
                </p>

            </div>

            <!-- MEDICINE BASE -->
            <div style="
                margin-top:35px;
            ">

                <h2 style="
                    color:#2563eb;
                    margin-bottom:15px;
                ">
                    Active Medicine Base: {current_base}
                </h2>

                <table width="100%" cellspacing="0" style="
                    border-collapse:collapse;
                    background:#ffffff;
                    border:1px solid #e5e7eb;
                    border-radius:14px;
                    overflow:hidden;
                ">

                    <tr style="
                        background:#eff6ff;
                    ">

                        <th style="
                            text-align:left;
                            padding:14px;
                            color:#1e3a8a;
                            font-size:14px;
                        ">
                            Current Medicines & Dosage
                        </th>

                    </tr>

                    {medicine_rows}

                </table>

            </div>

            <!-- DASHBOARD BUTTON -->
            <div style="
                text-align:center;
                margin-top:40px;
            ">

                <a href="https://patient-health-monitor.streamlit.app/"
                style="
                    background:#2563eb;
                    color:white;
                    padding:16px 28px;
                    border-radius:12px;
                    text-decoration:none;
                    font-weight:bold;
                    font-size:15px;
                    display:inline-block;
                ">
                    Open Full Dashboard
                </a>

            </div>

            <!-- FOOTER -->
            <div style="
                text-align:center;
                margin-top:35px;
                color:#9ca3af;
                font-size:12px;
            ">

                Generated Automatically by Patient Health Monitor System

            </div>

        </div>

    </div>

    </body>
    </html>

    """

    return html

# ======================================================
# 📧 SEND EMAIL USING RESEND API
# ======================================================
def send_email(report_text):

    url = "https://api.resend.com/emails"

    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }

    html_content = f"""
<html>
<body style="font-family: Arial; background:#f4f7fb; padding:20px;">

<div style="
max-width:700px;
margin:auto;
background:white;
padding:30px;
border-radius:12px;
box-shadow:0 4px 12px rgba(0,0,0,0.1);
">

<h1 style="color:#2563eb;">
Patient Health Monitor
</h1>

<p style="font-size:16px;">
Daily automated patient health report.
</p>

<hr>

<pre style="
font-size:16px;
line-height:1.8;
white-space:pre-wrap;
">
{report_text}
</pre>

<br><br>

<a href="https://patient-health-monitor.streamlit.app/"
style="
background:#2563eb;
color:white;
padding:12px 20px;
text-decoration:none;
border-radius:8px;
font-weight:bold;
display:inline-block;
">
Open Full Dashboard
</a>

</div>
</body>
</html>
"""

    data = {
        "from": "Health Monitor <onboarding@resend.dev>",
        "to": [TO_EMAIL],
        "subject": "📊 Daily Patient Health Report",
        "html": html_content
    }

    response = requests.post(url, json=data, headers=headers)

    print("Email Status:", response.status_code)
    print("Response:", response.text)

# ======================================================
# 🚀 MAIN EXECUTION
# ======================================================
if __name__ == "__main__":

    df = load_data()
    report = generate_html_report(df)

    print(report)
    send_email(report)
