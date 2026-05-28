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
    # Copy and paste this exact variable definition directly into your Python function:

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Patient Health Report</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f7f6; font-family: -apple-system, BlinkMacSystemFont, Arial, sans-serif;">

    <table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center" width="100%" style="background-color: #f4f7f6; padding: 20px 0;">
        <tr>
            <td>
                
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center" width="700" style="max-width: 700px; width: 100%; background-color: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
                    
                    <tr>
                        <td style="padding: 0;">
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td width="55%" style="padding: 25px; background-color: #ffffff; vertical-align: middle;">
                                        <span style="font-size: 26px; font-weight: bold; color: #1e3a8a;">💙 Health Monitor</span><br>
                                        <span style="font-size: 13px; color: #64748b; font-weight: 500; padding-left: 5px;">Remote Patient Monitoring</span>
                                    </td>
                                    <td width="45%" style="background-color: #004699; padding: 25px; text-align: right; vertical-align: middle; color: #ffffff;">
                                        <p style="margin: 0; font-size: 16px; font-weight: bold; letter-spacing: 0.5px;">📅 Daily Health Report</p>
                                        <p style="margin: 4px 0 0 0; font-size: 12px; color: #e2e8f0;">{current_date} • 07:00 AM (PKT)</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <tr>
                        <td style="padding: 20px 25px;">
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #edf2f7; border-radius: 8px; padding: 20px;">
                                <tr>
                                    <td style="vertical-align: middle;">
                                        <p style="margin: 0 0 6px 0; font-size: 18px; font-weight: bold; color: #1e293b;">Hello,</p>
                                        <p style="margin: 0; font-size: 14px; color: #475569; line-height: 1.5;">
                                            Here is your daily health summary. Your overall health status is 
                                            <span style="background-color: #bbf7d0; color: #166534; padding: 4px 10px; border-radius: 20px; font-weight: bold; font-size: 13px; display: inline-block; margin-left: 5px;">{health_status_tag} ✓</span>
                                        </p>
                                        <p style="margin: 8px 0 0 0; font-size: 13px; color: #64748b;">Stay consistent with your medicines and keep monitoring your health.</p>
                                    </td>
                                    <td width="80" align="right" style="vertical-align: middle; font-size: 45px;">🛡️</td>
                                    </tr>
                            </table>
                        </td>
                    </tr>

                    <tr>
                        <td style="padding: 10px 25px 5px 25px; font-size: 14px; font-weight: bold; color: #1e3a8a; text-transform: uppercase;">🩺 Today's Vitals Summary</td>
                    </tr>

                    <tr>
                        <td style="padding: 10px 25px 20px 25px;">
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td width="18%" style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 8px; text-align: center; background-color: #ffffff;">
                                        <span style="font-size: 11px; color: #475569; font-weight: 600;">❤️ Heart Rate</span>
                                        <p style="margin: 8px 0 2px 0; font-size: 20px; font-weight: bold; color: #0f172a;">{heart_rate} <span style="font-size: 11px; color: #64748b; font-weight: normal;">bpm</span></p>
                                        <span style="background-color: #dcfce7; color: #15803d; font-size: 10px; font-weight: bold; padding: 2px 6px; border-radius: 4px;">{heart_rate_status}</span>
                                        <p style="margin: 6px 0 0 0; font-size: 10px; color: #94a3b8;">(60-100 bpm)</p>
                                    </td>
                                    <td width="2%">&nbsp;</td>
                                    <td width="18%" style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 8px; text-align: center; background-color: #ffffff;">
                                        <span style="font-size: 11px; color: #475569; font-weight: 600;">🩺 Blood Pressure</span>
                                        <p style="margin: 8px 0 2px 0; font-size: 18px; font-weight: bold; color: #0f172a;">{bp_systolic}/{bp_diastolic}</p>
                                        <span style="background-color: #dcfce7; color: #15803d; font-size: 10px; font-weight: bold; padding: 2px 6px; border-radius: 4px;">{bp_status}</span>
                                        <p style="margin: 6px 0 0 0; font-size: 10px; color: #94a3b8;">(90/60-120/80)</p>
                                    </td>
                                    <td width="2%">&nbsp;</td>
                                    <td width="18%" style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 8px; text-align: center; background-color: #ffffff;">
                                        <span style="font-size: 11px; color: #475569; font-weight: 600;">🩸 Blood Glucose</span>
                                        <p style="margin: 8px 0 2px 0; font-size: 20px; font-weight: bold; color: #0f172a;">{blood_glucose} <span style="font-size: 10px; color: #64748b; font-weight: normal;">mg/dL</span></p>
                                        <span style="background-color: #dcfce7; color: #15803d; font-size: 10px; font-weight: bold; padding: 2px 6px; border-radius: 4px;">{glucose_status}</span>
                                        <p style="margin: 6px 0 0 0; font-size: 10px; color: #94a3b8;">(70-140 mg/dL)</p>
                                    </td>
                                    <td width="2%">&nbsp;</td>
                                    <td width="18%" style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 8px; text-align: center; background-color: #ffffff;">
                                        <span style="font-size: 11px; color: #475569; font-weight: 600;">💧 SpO2</span>
                                        <p style="margin: 8px 0 2px 0; font-size: 20px; font-weight: bold; color: #0f172a;">{spo2} <span style="font-size: 11px; color: #64748b; font-weight: normal;">%</span></p>
                                        <span style="background-color: #dcfce7; color: #15803d; font-size: 10px; font-weight: bold; padding: 2px 6px; border-radius: 4px;">{spo2_status}</span>
                                        <p style="margin: 6px 0 0 0; font-size: 10px; color: #94a3b8;">(95-100 %)</p>
                                    </td>
                                    <td width="2%">&nbsp;</td>
                                    <td width="18%" style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 8px; text-align: center; background-color: #ffffff;">
                                        <span style="font-size: 11px; color: #475569; font-weight: 600;">🌡️ Temp</span>
                                        <p style="margin: 8px 0 2px 0; font-size: 20px; font-weight: bold; color: #0f172a;">{temperature} <span style="font-size: 11px; color: #64748b; font-weight: normal;">°F</span></p>
                                        <span style="background-color: #dcfce7; color: #15803d; font-size: 10px; font-weight: bold; padding: 2px 6px; border-radius: 4px;">{temp_status}</span>
                                        <p style="margin: 6px 0 0 0; font-size: 10px; color: #94a3b8;">(97-99 °F)</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <tr>
                        <td style="padding: 10px 25px 20px 25px;">
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td width="58%" style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; vertical-align: top; background-color: #ffffff;">
                                        <span style="font-size: 13px; font-weight: bold; color: #1e3a8a; text-transform: uppercase;">📈 2. Vitals Trend (Last 7 Days)</span>
                                        <div style="margin-top: 15px; text-align: center;">
                                            <img src="{chart_image_url}" alt="7-Day Vitals Trend" width="100%" style="max-width: 350px; height: auto; border: 0; display: block; margin: 0 auto;">
                                        </div>
                                    </td>
                                    
                                    <td width="4%">&nbsp;</td>
                                    
                                    <td width="38%" style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; vertical-align: top; text-align: center; background-color: #ffffff;">
                                        <span style="font-size: 13px; font-weight: bold; color: #1e3a8a; text-transform: uppercase; display: block; text-align: left;">🎯 3. Health Score</span>
                                        <div style="margin: 20px auto 10px auto; width: 90px; height: 90px; border-radius: 50%; border: 8px solid #22c55e; border-left-color: #e2e8f0; line-height: 90px; text-align: center;">
                                            <span style="font-size: 26px; font-weight: bold; color: #0f172a;">{health_score}</span>
                                        </div>
                                        <span style="font-size: 11px; color: #64748b; display: block; margin-bottom: 5px;">/100</span>
                                        <p style="margin: 5px 0; font-size: 16px; font-weight: bold; color: #22c55e;">{health_score_rating}</p>
                                        <p style="margin: 0; font-size: 11px; color: #64748b;">You are doing well. Keep it up!</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <tr>
                        <td style="padding: 0 25px 20px 25px;">
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td width="48%" style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; background-color: #ffffff; vertical-align: middle;">
                                        <span style="font-size: 12px; font-weight: bold; color: #1e3a8a; text-transform: uppercase; display: block; margin-bottom: 10px;">📋 4. Medicine Adherence</span>
                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; padding: 10px;">
                                            <tr>
                                                <td width="30" style="font-size: 20px; text-align: center; vertical-align: middle;">✅</td>
                                                <td>
                                                    <p style="margin: 0; font-size: 12px; font-weight: bold; color: #14532d;">All medications taken on time</p>
                                                    <p style="margin: 2px 0 0 0; font-size: 11px; color: #166534;">Keep following your schedule.</p>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>

                                    <td width="4%">&nbsp;</td>

                                    <td width="48%" style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; background-color: #ffffff; vertical-align: middle;">
                                        <span style="font-size: 12px; font-weight: bold; color: #1e3a8a; text-transform: uppercase; display: block; margin-bottom: 10px;">🔔 5. Alerts & Notifications</span>
                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-
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
