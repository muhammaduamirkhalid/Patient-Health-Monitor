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

    # Sort latest data
    df = df.sort_values("created_at")

    # Calculate health score
    df["health_score"] = df.apply(calculate_score, axis=1)

    # Latest patient reading
    latest = df.iloc[-1]

    # =========================================
    # FETCH CURRENT MEDICINE BASE
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

    # Convert comma-separated medicines into table rows
    medicine_rows = ""

    for med in medicines_text.split(","):
        medicine_rows += f"""
        <tr>
            <td style="padding:10px; border:1px solid #ddd;">{med.strip()}</td>
        </tr>
        """

    # =========================================
    # HEALTH STATUS COLOR
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
    # HTML EMAIL TEMPLATE
    # =========================================
    html = f"""
    <html>
    <body style="
        font-family: Arial, sans-serif;
        background:#f4f7fb;
        padding:20px;
    ">

    <div style="
        max-width:800px;
        margin:auto;
        background:white;
        border-radius:16px;
        overflow:hidden;
        box-shadow:0 4px 12px rgba(0,0,0,0.1);
    ">

        <!-- HEADER -->
        <div style="
            background:#2563eb;
            color:white;
            padding:30px;
            text-align:center;
        ">
            <h1>Patient Health Monitor</h1>
            <p>Daily Automated Health Report</p>
        </div>

        <!-- HEALTH STATUS -->
        <div style="padding:25px;">

            <div style="
                background:{status_color};
                color:white;
                padding:15px;
                border-radius:12px;
                text-align:center;
                font-size:22px;
                font-weight:bold;
            ">
                Health Score: {health_score}/100 — {status_text}
            </div>

            <br>

            <!-- VITALS -->
            <h2 style="color:#2563eb;">Latest Vitals</h2>

            <table width="100%" cellspacing="0" style="
                border-collapse:collapse;
                margin-top:10px;
            ">

                <tr>
                    <td style="padding:12px; border:1px solid #ddd;">
                        Pulse
                    </td>

                    <td style="padding:12px; border:1px solid #ddd;">
                        {latest['pulse']} BPM
                    </td>
                </tr>

                <tr>
                    <td style="padding:12px; border:1px solid #ddd;">
                        Blood Pressure
                    </td>

                    <td style="padding:12px; border:1px solid #ddd;">
                        {latest['systolic']}/{latest['diastolic']}
                    </td>
                </tr>

                <tr>
                    <td style="padding:12px; border:1px solid #ddd;">
                        SpO2
                    </td>

                    <td style="padding:12px; border:1px solid #ddd;">
                        {latest['spo2']}%
                    </td>
                </tr>

            </table>

            <br>

            <!-- MEDICINE BASE -->
            <h2 style="color:#2563eb;">
                Current Medicine Base: {current_base}
            </h2>

            <table width="100%" cellspacing="0" style="
                border-collapse:collapse;
                margin-top:10px;
            ">

                <tr style="background:#eff6ff;">
                    <th style="padding:12px; border:1px solid #ddd;">
                        Current Medicines
                    </th>
                </tr>

                {medicine_rows}

            </table>

            <br><br>

            <!-- DASHBOARD BUTTON -->
            <div style="text-align:center;">

                <a href="https://patient-health-monitor.streamlit.app/"
                style="
                    background:#2563eb;
                    color:white;
                    padding:14px 24px;
                    text-decoration:none;
                    border-radius:10px;
                    font-weight:bold;
                    display:inline-block;
                ">
                    Open Full Dashboard
                </a>

            </div>

            <br>

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
    report = generate_report(df)

    print(report)
    send_email(report)
