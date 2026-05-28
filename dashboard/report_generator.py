# ======================================================
# 📊 PATIENT HEALTH REPORT GENERATOR
# ======================================================

import os
import pandas as pd
import requests
from supabase import create_client
from datetime import datetime

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

    # =====================================================
    # SORT DATA
    # =====================================================
    df = df.sort_values("created_at")

    # =====================================================
    # HEALTH SCORE
    # =====================================================
    df["health_score"] = df.apply(calculate_score, axis=1)

    latest = df.iloc[-1]

    # =====================================================
    # CURRENT MEDICINE BASE
    # =====================================================
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

    # =====================================================
    # MEDICINE TABLE ROWS
    # =====================================================
    medicine_rows = ""

    for med in medicines_text.split(","):

        medicine_rows += f"""
        <tr>
            <td style="padding:14px;border-bottom:1px solid #e5e7eb;">
                {med.strip()}
            </td>

            <td style="padding:14px;border-bottom:1px solid #e5e7eb;">
                Monitoring
            </td>

            <td style="padding:14px;border-bottom:1px solid #e5e7eb;">
                Effective
            </td>
        </tr>
        """

    # =====================================================
    # HEALTH STATUS
    # =====================================================
    health_score = latest["health_score"]

    if health_score >= 80:
        status_color = "#16a34a"
        status_text = "Good"

    elif health_score >= 60:
        status_color = "#f59e0b"
        status_text = "Warning"

    else:
        status_color = "#dc2626"
        status_text = "Critical"

    # =====================================================
    # ALERT TEXT
    # =====================================================
    alert_text = "No critical alerts today"

    if latest["spo2"] < 95:
        alert_text = "SpO2 level below safe threshold"

    if latest["systolic"] > 140:
        alert_text = "Blood pressure elevated"

    # =====================================================
    # HTML TEMPLATE
    # =====================================================
    html = f"""
    <html>

    <body style="
        margin:0;
        padding:30px;
        background:#f3f4f6;
        font-family:Arial,sans-serif;
    ">

    <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
    <td align="center">

    <table width="100%" cellpadding="0" cellspacing="0"
    style="
        max-width:1000px;
        background:white;
        border-radius:18px;
        overflow:hidden;
        box-shadow:0 8px 25px rgba(0,0,0,0.08);
    ">

    <!-- ================================================= -->
    <!-- HEADER -->
    <!-- ================================================= -->

    <tr>
    <td>

    <table width="100%" cellpadding="0" cellspacing="0">

    <tr>

        <td width="55%"
        style="
            background:#ffffff;
            padding:30px;
        ">

            <div style="
                font-size:46px;
                color:#2563eb;
                font-weight:bold;
                display:inline-block;
                vertical-align:middle;
            ">
                ❤
            </div>

            <div style="
                display:inline-block;
                margin-left:14px;
                vertical-align:middle;
            ">

                <div style="
                    font-size:24px;
                    font-weight:bold;
                    color:#1d4ed8;
                ">
                    Health Monitor
                </div>

                <div style="
                    color:#6b7280;
                    font-size:15px;
                    margin-top:4px;
                ">
                    Remote Patient Monitoring
                </div>

            </div>

        </td>

        <td width="45%"
        style="
            background:linear-gradient(135deg,#1d4ed8,#1e3a8a);
            padding:30px;
            color:white;
        ">

            <div style="
                font-size:30px;
                margin-bottom:10px;
            ">
                📅
            </div>

            <div style="
                font-size:20px;
                font-weight:bold;
            ">
                Daily Health Report
            </div>

            <div style="
                margin-top:10px;
                opacity:0.95;
                font-size:15px;
            ">
                Automated Monitoring System
            </div>

        </td>

    </tr>

    </table>

    </td>
    </tr>

    <!-- ================================================= -->
    <!-- GREETING SECTION -->
    <!-- ================================================= -->

    <tr>
    <td style="padding:22px;">

    <table width="100%" cellpadding="0" cellspacing="0"
    style="
        background:#f8fafc;
        border:1px solid #dbeafe;
        border-radius:16px;
    ">

    <tr>

        <td style="padding:28px;">

            <div style="
                font-size:28px;
                font-weight:bold;
                color:#1e3a8a;
                margin-bottom:16px;
            ">
                Hello,
            </div>

            <div style="
                font-size:18px;
                color:#374151;
                line-height:1.8;
            ">
                Here is your daily health summary.
                Your overall health status is
                <span style="
                    background:#dcfce7;
                    color:#15803d;
                    padding:8px 14px;
                    border-radius:10px;
                    font-weight:bold;
                    margin-left:6px;
                ">
                    {status_text}
                </span>
            </div>

            <div style="
                margin-top:18px;
                color:#4b5563;
                font-size:15px;
            ">
                Stay consistent with your medicines and keep monitoring your health.
            </div>

        </td>

        <td width="120" align="center">

            <div style="
                font-size:72px;
                color:#60a5fa;
            ">
                🛡
            </div>

        </td>

    </tr>

    </table>

    </td>
    </tr>

    <!-- ================================================= -->
    <!-- VITALS SECTION -->
    <!-- ================================================= -->

    <tr>
    <td style="padding:0 22px 22px 22px;">

    <div style="
        font-size:30px;
        font-weight:bold;
        color:#1e3a8a;
        margin-bottom:22px;
    ">
        Today's Vitals Summary
    </div>

    <table width="100%" cellpadding="10" cellspacing="0">

    <tr>

    <!-- HEART RATE -->

    <td width="33%">

    <table width="100%" cellpadding="0" cellspacing="0"
    style="
        background:white;
        border:1px solid #e5e7eb;
        border-radius:16px;
    ">

    <tr>
    <td style="padding:22px;text-align:center;">

        <div style="font-size:42px;">❤</div>

        <div style="
            margin-top:10px;
            color:#6b7280;
            font-size:16px;
        ">
            Heart Rate
        </div>

        <div style="
            margin-top:18px;
            font-size:42px;
            font-weight:bold;
            color:#111827;
        ">
            {latest['pulse']}
        </div>

        <div style="
            margin-top:6px;
            color:#6b7280;
            font-size:16px;
        ">
            bpm
        </div>

        <div style="
            margin-top:18px;
            display:inline-block;
            background:#dcfce7;
            color:#15803d;
            padding:8px 16px;
            border-radius:10px;
            font-weight:bold;
        ">
            Normal
        </div>

        <div style="
            margin-top:14px;
            color:#6b7280;
            font-size:14px;
        ">
            (60 – 100 bpm)
        </div>

    </td>
    </tr>

    </table>

    </td>

    <!-- BLOOD PRESSURE -->

    <td width="33%">

    <table width="100%" cellpadding="0" cellspacing="0"
    style="
        background:white;
        border:1px solid #e5e7eb;
        border-radius:16px;
    ">

    <tr>
    <td style="padding:22px;text-align:center;">

        <div style="font-size:42px;">🩺</div>

        <div style="
            margin-top:10px;
            color:#6b7280;
            font-size:16px;
        ">
            Blood Pressure
        </div>

        <div style="
            margin-top:18px;
            font-size:36px;
            font-weight:bold;
            color:#111827;
        ">
            {latest['systolic']}/{latest['diastolic']}
        </div>

        <div style="
            margin-top:6px;
            color:#6b7280;
            font-size:16px;
        ">
            mmHg
        </div>

        <div style="
            margin-top:18px;
            display:inline-block;
            background:#dcfce7;
            color:#15803d;
            padding:8px 16px;
            border-radius:10px;
            font-weight:bold;
        ">
            Normal
        </div>

        <div style="
            margin-top:14px;
            color:#6b7280;
            font-size:14px;
        ">
            (90/60 – 120/80)
        </div>

    </td>
    </tr>

    </table>

    </td>

    <!-- SPO2 -->

    <td width="33%">

    <table width="100%" cellpadding="0" cellspacing="0"
    style="
        background:white;
        border:1px solid #e5e7eb;
        border-radius:16px;
    ">

    <tr>
    <td style="padding:22px;text-align:center;">

        <div style="font-size:42px;">🫁</div>

        <div style="
            margin-top:10px;
            color:#6b7280;
            font-size:16px;
        ">
            SpO2
        </div>

        <div style="
            margin-top:18px;
            font-size:42px;
            font-weight:bold;
            color:#111827;
        ">
            {latest['spo2']}
        </div>

        <div style="
            margin-top:6px;
            color:#6b7280;
            font-size:16px;
        ">
            %
        </div>

        <div style="
            margin-top:18px;
            display:inline-block;
            background:#dcfce7;
            color:#15803d;
            padding:8px 16px;
            border-radius:10px;
            font-weight:bold;
        ">
            Normal
        </div>

        <div style="
            margin-top:14px;
            color:#6b7280;
            font-size:14px;
        ">
            (95 – 100%)
        </div>

    </td>
    </tr>

    </table>

    </td>

    </tr>

    </table>

    <!-- ================================================= -->
    <!-- FUTURE CARDS -->
    <!-- ================================================= -->

    <!--
    ADD GLUCOSE CARD HERE LATER
    ADD TEMPERATURE CARD HERE LATER
    -->

    </td>
    </tr>

    <!-- ================================================= -->
    <!-- HEALTH SCORE + ALERTS -->
    <!-- ================================================= -->

    <tr>
    <td style="padding:0 22px 22px 22px;">

    <table width="100%" cellpadding="12" cellspacing="0">

    <tr>

    <!-- HEALTH SCORE -->

    <td width="50%">

    <table width="100%" cellpadding="0" cellspacing="0"
    style="
        background:white;
        border:1px solid #e5e7eb;
        border-radius:16px;
    ">

    <tr>
    <td style="padding:30px;text-align:center;">

        <div style="
            font-size:26px;
            font-weight:bold;
            color:#1e3a8a;
            margin-bottom:24px;
        ">
            Health Score
        </div>

        <div style="
            width:180px;
            height:180px;
            border-radius:50%;
            border:18px solid #22c55e;
            margin:auto;
            line-height:145px;
            font-size:58px;
            font-weight:bold;
            color:#111827;
        ">
            {health_score}
        </div>

        <div style="
            margin-top:20px;
            color:#16a34a;
            font-size:36px;
            font-weight:bold;
        ">
            {status_text}
        </div>

    </td>
    </tr>

    </table>

    </td>

    <!-- ALERTS -->

    <td width="50%">

    <table width="100%" cellpadding="0" cellspacing="0"
    style="
        background:white;
        border:1px solid #e5e7eb;
        border-radius:16px;
    ">

    <tr>
    <td style="padding:30px;">

        <div style="
            font-size:26px;
            font-weight:bold;
            color:#1e3a8a;
            margin-bottom:26px;
        ">
            Alerts & Notifications
        </div>

        <table width="100%" cellpadding="0" cellspacing="0"
        style="
            background:#f0fdf4;
            border:1px solid #bbf7d0;
            border-radius:14px;
        ">

        <tr>

            <td width="70" align="center"
            style="padding:20px;font-size:42px;">
                ✔
            </td>

            <td style="padding:20px;">

                <div style="
                    font-size:20px;
                    font-weight:bold;
                    color:#166534;
                ">
                    {alert_text}
                </div>

                <div style="
                    margin-top:10px;
                    color:#4b5563;
                    font-size:15px;
                ">
                    All vitals are being monitored continuously.
                </div>

            </td>

        </tr>

        </table>

    </td>
    </tr>

    </table>

    </td>

    </tr>

    </table>

    </td>
    </tr>

    <!-- ================================================= -->
    <!-- MEDICINE TABLE -->
    <!-- ================================================= -->

    <tr>
    <td style="padding:0 22px 22px 22px;">

    <div style="
        font-size:30px;
        font-weight:bold;
        color:#1e3a8a;
        margin-bottom:18px;
    ">
        Medicine Impact Summary
    </div>

    <table width="100%" cellpadding="0" cellspacing="0"
    style="
        border-collapse:collapse;
        background:white;
        border:1px solid #e5e7eb;
        border-radius:16px;
        overflow:hidden;
    ">

    <tr style="
        background:#1d4ed8;
        color:white;
    ">

        <th style="padding:16px;text-align:left;">
            Medicine Name
        </th>

        <th style="padding:16px;text-align:left;">
            Purpose
        </th>

        <th style="padding:16px;text-align:left;">
            Status
        </th>

    </tr>

    {medicine_rows}

    </table>

    </td>
    </tr>

    <!-- ================================================= -->
    <!-- DASHBOARD BUTTON -->
    <!-- ================================================= -->

    <tr>
    <td align="center" style="padding:10px 20px 30px 20px;">

    <a href="https://patient-health-monitor.streamlit.app/"
    style="
        background:#2563eb;
        color:white;
        padding:18px 34px;
        border-radius:14px;
        text-decoration:none;
        font-size:18px;
        font-weight:bold;
        display:inline-block;
    ">
        Open Full Dashboard
    </a>

    </td>
    </tr>

    <!-- ================================================= -->
    <!-- FOOTER -->
    <!-- ================================================= -->

    <tr>
    <td style="padding:0 22px 30px 22px;">

    <table width="100%" cellpadding="0" cellspacing="0"
    style="
        background:#eff6ff;
        border-radius:16px;
    ">

    <tr>

        <td style="padding:24px;">

            <div style="
                font-size:26px;
                color:#2563eb;
                margin-bottom:12px;
            ">
                💙 Tip of the Day
            </div>

            <div style="
                color:#4b5563;
                font-size:16px;
                line-height:1.8;
            ">
                Drink enough water, take your medicines on time,
                and keep moving. Small steps lead to big results.
            </div>

        </td>

        <td width="260" style="padding:24px;">

            <div style="
                font-size:28px;
                font-weight:bold;
                color:#1d4ed8;
                margin-bottom:10px;
            ">
                Stay healthy, stay happy!
            </div>

            <div style="
                color:#111827;
                font-size:18px;
            ">
                — Your Health Monitor System
            </div>

        </td>

    </tr>

    </table>

    </td>
    </tr>

    <!-- ================================================= -->
    <!-- FINAL FOOTER -->
    <!-- ================================================= -->

    <tr>
    <td align="center"
    style="
        padding-bottom:30px;
        color:#9ca3af;
        font-size:14px;
    ">

    This is an automated report. Please do not reply to this email.

    </td>
    </tr>

    </table>

    </td>
    </tr>
    </table>

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
