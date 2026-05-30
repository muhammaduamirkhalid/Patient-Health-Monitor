
# ======================================================
# 📊 PATIENT HEALTH REPORT GENERATOR
# IMAGE BASED VERSION
# ======================================================

import os
import pandas as pd
import requests
import matplotlib.pyplot as plt

from supabase import create_client
from matplotlib.patches import FancyBboxPatch

import base64
import mimetypes

# ======================================================
# 🔐 LOAD ENV VARIABLES
# ======================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

TO_EMAIL = "pakistanijrl@gmail.com"

# ======================================================
# 🔌 CONNECT SUPABASE
# ======================================================

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ======================================================
# 📥 LOAD DATA
# ======================================================

def load_data():

    res = supabase.table("patient_readings").select("*").execute()

    df = pd.DataFrame(res.data)

    if df.empty:
        return df

    df["created_at"] = pd.to_datetime(df["created_at"])

    return df

# ======================================================
# 🧠 HEALTH SCORE
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
# 🎨 GENERATE DASHBOARD IMAGE
# ======================================================

def generate_html_report(df):

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
    # AVERAGES
    # =========================================

    avg_pulse = round(df["pulse"].astype(float).mean(), 1)

    avg_sys = round(df["systolic"].astype(float).mean(), 1)

    avg_dia = round(df["diastolic"].astype(float).mean(), 1)

    avg_spo2 = round(df["spo2"].astype(float).mean(), 1)

    # =========================================
    # HEALTH STATUS
    # =========================================

    health_score = latest["health_score"]

    if health_score >= 80:
        status = "GOOD"
        status_color = "#16a34a"

    elif health_score >= 60:
        status = "WARNING"
        status_color = "#f59e0b"

    else:
        status = "CRITICAL"
        status_color = "#dc2626"

    # =========================================
    # CREATE FIGURE
    # =========================================

    fig = plt.figure(figsize=(14, 9))

    fig.patch.set_facecolor("#eef4ff")

    ax = plt.axes([0, 0, 1, 1])

    ax.axis("off")

    # =========================================
    # MAIN CONTAINER
    # =========================================

    container = FancyBboxPatch(
        (0.03, 0.04),
        0.94,
        0.92,
        boxstyle="round,pad=0.015,rounding_size=0.02",
        facecolor="white",
        edgecolor="none"
    )

    ax.add_patch(container)

    # =========================================
    # HEADER
    # =========================================

    header = FancyBboxPatch(
        (0.03, 0.84),
        0.94,
        0.12,
        boxstyle="round,pad=0.015,rounding_size=0.02",
        facecolor="#2563eb",
        edgecolor="none"
    )

    ax.add_patch(header)

    ax.text(
        0.08,
        0.90,
        "❤",
        fontsize=36,
        color="white",
        fontweight="bold"
    )

    ax.text(
        0.14,
        0.91,
        "Health Monitor",
        fontsize=26,
        color="white",
        fontweight="bold"
    )

    ax.text(
        0.14,
        0.875,
        "Daily Patient Health Report",
        fontsize=13,
        color="white"
    )

    # =========================================
    # STATUS PANEL
    # =========================================

    status_box = FancyBboxPatch(
        (0.08, 0.73),
        0.84,
        0.08,
        boxstyle="round,pad=0.02,rounding_size=0.02",
        facecolor=status_color,
        edgecolor="none"
    )

    ax.add_patch(status_box)

    ax.text(
        0.5,
        0.765,
        f"CURRENT HEALTH STATUS : {status}",
        fontsize=20,
        color="white",
        ha="center",
        fontweight="bold"
    )

    # =========================================
    # CARD FUNCTION
    # =========================================

    def create_card(x, y, title, value, subtitle):

        card = FancyBboxPatch(
            (x, y),
            0.19,
            0.16,
            boxstyle="round,pad=0.02,rounding_size=0.02",
            facecolor="#f8fafc",
            edgecolor="#dbeafe"
        )

        ax.add_patch(card)

        ax.text(
            x + 0.095,
            y + 0.115,
            title,
            fontsize=13,
            ha="center",
            color="#6b7280"
        )

        ax.text(
            x + 0.095,
            y + 0.07,
            value,
            fontsize=24,
            ha="center",
            color="#111827",
            fontweight="bold"
        )

        ax.text(
            x + 0.095,
            y + 0.03,
            subtitle,
            fontsize=11,
            ha="center",
            color="#6b7280"
        )

    # =========================================
    # LATEST RESULT CARDS
    # =========================================

    create_card(
        0.08,
        0.50,
        "Pulse",
        f"{latest['pulse']}",
        "Latest BPM"
    )

    create_card(
        0.30,
        0.50,
        "Blood Pressure",
        f"{latest['systolic']}/{latest['diastolic']}",
        "Latest mmHg"
    )

    create_card(
        0.52,
        0.50,
        "SpO2",
        f"{latest['spo2']}%",
        "Latest Oxygen"
    )

    create_card(
        0.74,
        0.50,
        "Health Score",
        f"{health_score}",
        "/100"
    )

    # =========================================
    # AVERAGE SECTION TITLE
    # =========================================

    ax.text(
        0.08,
        0.43,
        "Average Health Statistics",
        fontsize=22,
        color="#1e3a8a",
        fontweight="bold"
    )

    # =========================================
    # AVERAGE CARDS
    # =========================================

    create_card(
        0.08,
        0.22,
        "Average Pulse",
        f"{avg_pulse}",
        "BPM"
    )

    create_card(
        0.30,
        0.22,
        "Average BP",
        f"{avg_sys}/{avg_dia}",
        "mmHg"
    )

    create_card(
        0.52,
        0.22,
        "Average SpO2",
        f"{avg_spo2}%",
        "Oxygen"
    )

    create_card(
        0.74,
        0.22,
        "Medicine Base",
        latest["medicine_base"],
        "Current Base"
    )

    # =========================================
    # FOOTER
    # =========================================

    ax.text(
        0.5,
        0.10,
        "Generated Automatically by Patient Health Monitor",
        fontsize=12,
        ha="center",
        color="#6b7280"
    )

    # =========================================
    # SAVE IMAGE
    # =========================================

    image_path = "health_report.png"

    plt.savefig(
        image_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    return image_path

# ======================================================
# 📧 SEND EMAIL
# ======================================================

def send_email(image_path):

    url = "https://api.resend.com/emails"

    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }

    html = f"""
    <html>

    <body style="font-family:Arial,sans-serif;">

        <h2>Daily Patient Health Report</h2>

        <p>
        Your latest patient monitoring report is attached below.
        </p>

        <img src="cid:health_report" width="100%">

        <br><br>

        <a href="https://patient-health-monitor.streamlit.app/">
            Open Full Dashboard
        </a>

    </body>

    </html>
    """

    files = {
        "attachments": open(image_path, "rb")
    }
    with open(image_path, "rb") as f:
    image_content = base64.b64encode(f.read()).decode("utf-8")
    
    data = {
    "from": "Health Monitor <onboarding@resend.dev>",
    "to": [TO_EMAIL],
    "subject": "📊 Daily Patient Health Report",

    "html": """
    <h2>Daily Patient Health Report</h2>

    <p>
    The dashboard report is attached to this email.
    </p>

    <p>
    Dashboard:
    https://patient-health-monitor.streamlit.app/
    </p>
    """,

    "attachments": [
        {
            "filename": "health_report.png",
            "content": image_content
        }
    ]
}

    response = requests.post(
    url,
    json=data,
    headers=headers
)

    print("Email Status:", response.status_code)
    print("Response:", response.text)

# ======================================================
# 🚀 MAIN
# ======================================================

if __name__ == "__main__":

    df = load_data()

    image_path = generate_html_report(df)
    print("Generated image:", image_path)
    send_email(image_path)
    
