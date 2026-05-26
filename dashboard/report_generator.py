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
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Patient Health Report</title>
    <style>
        :root {
            --primary-blue: #1a4a8d;
            --light-blue: #f0f7ff;
            --success-green: #28a745;
            --text-dark: #333;
            --border-color: #e1e8ed;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f4f7f6;
            color: var(--text-dark);
            margin: 0;
            padding: 20px;
        }

        .report-container {
            max-width: 850px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }

        /* Header Section */
        header {
            display: flex;
            justify-content: space-between;
            padding: 20px;
            border-bottom: 1px solid var(--border-color);
        }

        .logo-section {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .header-info {
            background-color: var(--primary-blue);
            color: white;
            padding: 15px 25px;
            border-radius: 5px;
            text-align: right;
        }

        /* Status Banner */
        .status-banner {
            background-color: var(--light-blue);
            padding: 20px;
            margin: 20px;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .status-badge {
            background: var(--success-green);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
        }

        /* Grid Layouts */
        .vitals-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            padding: 0 20px;
        }

        .vital-card {
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }

        .vital-value {
            font-size: 1.4em;
            font-weight: bold;
            margin: 10px 0;
        }

        .normal-tag {
            color: var(--success-green);
            font-size: 0.85em;
            font-weight: bold;
        }

        /* Table Styles */
        .medicine-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }

        .medicine-table th {
            background-color: var(--primary-blue);
            color: white;
            text-align: left;
            padding: 12px;
        }

        .medicine-table td {
            padding: 12px;
            border-bottom: 1px solid var(--border-color);
        }

        section {
            padding: 20px;
        }

        h2 {
            font-size: 1.1em;
            color: var(--primary-blue);
            border-bottom: 2px solid var(--light-blue);
            padding-bottom: 5px;
            text-transform: uppercase;
        }

        .flex-row {
            display: flex;
            gap: 20px;
        }

        .flex-1 { flex: 1; }

        footer {
            text-align: center;
            font-size: 0.8em;
            color: #777;
            padding: 20px;
            border-top: 1px solid var(--border-color);
        }
    </style>
</head>
<body>

<div class="report-container">
    <header>
        <div class="logo-section">
            <div style="font-size: 2em; color: var(--primary-blue);">✚</div>
            <div>
                <h1 style="margin:0; font-size: 1.5em; color: var(--primary-blue);">Health Monitor</h1>
                <small>Remote Patient Monitoring</small>
            </div>
        </div>
        <div class="header-info">
            <div>Daily Health Report</div>
            <div style="font-size: 0.8em;">May 21, 2025 • 07:00 AM (PKT)</div>
        </div>
    </header>

    <div class="status-banner">
        <div>
            <h3 style="margin:0;">Hello,</h3>
            <p style="margin: 5px 0;">Your overall health status is <span class="status-badge">Good ✓</span></p>
            <small>Stay consistent with your medicines and keep monitoring your health.</small>
        </div>
    </div>

    <section>
        <h2>Today's Vitals Summary</h2>
        <div class="vitals-grid">
            <div class="vital-card">
                <div style="color: #e74c3c;">❤️ Heart Rate</div>
                <div class="vital-value">72 <small>bpm</small></div>
                <div class="normal-tag">Normal</div>
                <small>(60 - 100 bpm)</small>
            </div>
            <div class="vital-card">
                <div style="color: #3498db;">🩺 Blood Pressure</div>
                <div class="vital-value">118/76 <small>mmHg</small></div>
                <div class="normal-tag">Normal</div>
                <small>(90/60 - 120/80)</small>
            </div>
            <div class="vital-card">
                <div style="color: #f39c12;">💧 Blood Glucose</div>
                <div class="vital-value">104 <small>mg/dL</small></div>
                <div class="normal-tag">Normal</div>
                <small>(70 - 140 mg/dL)</small>
            </div>
            <div class="vital-card">
                <div style="color: #9b59b6;">☁️ SpO2</div>
                <div class="vital-value">98 <small>%</small></div>
                <div class="normal-tag">Normal</div>
                <small>(95 - 100 %)</small>
            </div>
            <div class="vital-card">
                <div style="color: #27ae60;">🌡️ Temperature</div>
                <div class="vital-value">98.4 <small>°F</small></div>
                <div class="normal-tag">Normal</div>
                <small>(97 - 99 °F)</small>
            </div>
        </div>
    </section>

    <div class="flex-row" style="padding: 0 20px;">
        <section class="flex-1">
            <h2>2. Vitals Trend (Last 7 Days)</h2>
            <div style="height: 150px; background: #fafafa; border: 1px dashed #ccc; display: flex; align-items: center; justify-content: center; color: #999;">
                [Graph: Stable trends for HR, BP, and Glucose]
            </div>
        </section>
        <section style="width: 250px; text-align: center;">
            <h2>3. Health Score</h2>
            <div style="font-size: 3em; color: var(--success-green); font-weight: bold; margin: 10px 0;">85<small style="font-size: 0.4em;">/100</small></div>
            <div class="status-badge" style="display: inline-block;">Good</div>
            <p><small>You are doing well. Keep it up!</small></p>
        </section>
    </div>

    <div class="flex-row" style="padding: 0 20px;">
        <section class="flex-1" style="background: #f9f9f9; margin: 10px; border-radius: 8px;">
            <h3>4. Medicine Adherence</h3>
            <p>✅ All medications taken on time</p>
        </section>
        <section class="flex-1" style="background: #f9f9f9; margin: 10px; border-radius: 8px;">
            <h3>5. Alerts & Notifications</h3>
            <p>🔔 No critical alerts today</p>
        </section>
    </div>

    <section>
        <h2>6. Medicine Impact Summary</h2>
        <table class="medicine-table">
            <thead>
                <tr>
                    <th>Medicine Name</th>
                    <th>Purpose</th>
                    <th>Impact</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Amlodipine 5mg</td>
                    <td>Blood Pressure</td>
                    <td>Stabilizing BP</td>
                    <td class="normal-tag">Effective</td>
                </tr>
                <tr>
                    <td>Metformin 500mg</td>
                    <td>Blood Sugar</td>
                    <td>Improving Glucose</td>
                    <td class="normal-tag">Effective</td>
                </tr>
                <tr>
                    <td>Atorvastatin 10mg</td>
                    <td>Cholesterol</td>
                    <td>Improving Lipid Profile</td>
                    <td class="normal-tag">Effective</td>
                </tr>
            </tbody>
        </table>
    </section>

    <footer style="background-color: var(--light-blue); margin-top: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 0 20px;">
            <div style="text-align: left;">
                <strong>Tip of the Day</strong><br>
                <small>Drink enough water, take your medicines on time, and keep moving.</small>
            </div>
            <div style="text-align: right;">
                Stay healthy, stay happy!<br>
                <strong>- Your Health Monitor System</strong>
            </div>
        </div>
        <p style="margin-top: 20px; font-size: 0.7em;">This is an automated report. Please do not reply to this email.</p>
    </footer>
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
