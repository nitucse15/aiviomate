import re
import os
import json
import time
from io import BytesIO
from datetime import date
import cv2
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import base64
from ai_engine import (
    generate_workout,
    generate_diet,
    coach_reply,
    stress_relief,
    generate_zumba,
    generate_eye_care,
)
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# =========================
# PAGE CONFIG (MUST BE FIRST)
# =========================
st.set_page_config(layout="wide")
LOGO_URL = "https://imgcdn.stablediffusionweb.com/2025/8/29/c87b3fbd-f0fc-46c6-9334-a431484cc041.jpg"

st.markdown(
    f"""
    <style>

    .top-right-logo {{
        position: absolute;
        top: 55px;
        right: 25px;
        z-index: 99999;
    }}

    .top-right-logo img {{
        width: 100px;
        height: 100px;
        border-radius: 80%;
        object-fit: cover;
        border: 2px solid rgba(255,255,255,0.15);
        box-shadow: 0 0 20px rgba(139,92,246,0.45);
    }}

    </style>

    <div class="top-right-logo">
        <img src="{LOGO_URL}">
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
<style>

/* Expander header */
.streamlit-expanderHeader {
    background-color: #081028 !important;
    color: white !important;
    border-radius: 10px !important;
}

/* Expanded content */
.streamlit-expanderContent {
    background-color: #081028 !important;
    color: white !important;
    border-radius: 10px !important;
}

/* Entire expander */
details {
    background-color: #081028 !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.08);
}

</style>
""",
    unsafe_allow_html=True,
)

# =========================
# GLOBAL CSS
# =========================
st.markdown(
    """
<style>
div.stDownloadButton > button {
    background-color: #6C63FF !important;
    color: white !important;
    border-radius: 8px;
    font-weight: 600;
}
</style>
""",
    unsafe_allow_html=True,
)
st.markdown(
    """
<style>

/* ===== App Background ===== */
.stApp {
    background: linear-gradient(135deg, #0f172a, #111827);
    color: white;
}

div[data-testid="stFileUploader"] {
    background-color: transparent !important;
}

/* ===== Section Cards ===== */
.card {
    background: rgba(255,255,255,0.06);
    padding: 16px;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(8px);
}

/* ===== Headings ===== */
h1, h2, h3, h4, label {
    color: white !important;
}

/* ===== Buttons ===== */
.stButton button {
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    color: white !important;
    border-radius: 10px;
    height: 48px;
    width: 100% !important;
    border: none;
    font-weight: 600;
    transition: all 0.25s ease;
}

.stButton button:hover {
    background: linear-gradient(90deg, #4f46e5, #7c3aed);
}

/* ===== Sliders ===== */
.stSlider label {
    color: #ddd;
}

/* ===== INPUT BOX DARK THEME ===== */
input, textarea {
    background-color: #0e2a47 !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 10px !important;
}

input::placeholder {
    color: #aaa !important;
}

div[data-baseweb="input"] > div {
    background-color: #0e2a47 !important;
    border-radius: 10px;
}

div[data-baseweb="input"] input:focus {
    outline: none !important;
    border: 1px solid #6366f1 !important;
}

/* ===== Dropdowns ===== */
div[data-baseweb="select"] > div {
    background-color: #0e2a47 !important;
    color: white !important;
    border-radius: 8px;
}

/* ===== Images ===== */
img {
    border-radius: 14px;
    object-fit: cover;
}

/* ===== Progress Bar ===== */
.stProgress > div > div {
    background: linear-gradient(90deg, #22c55e, #4ade80);
}

/* ===== Chat Bubbles ===== */
.user-bubble {
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    padding: 10px 14px;
    border-radius: 12px;
    color: white;
    margin: 8px 0;
    width: fit-content;
    margin-left: auto;
}

.bot-bubble {
    background: rgba(255,255,255,0.08);
    padding: 10px 14px;
    border-radius: 12px;
    color: white;
    margin: 8px 0;
    width: fit-content;
}

/* ===== Remove old conflicts ===== */
.stat-card {
    display: none;
}
</style>
""",
    unsafe_allow_html=True,
)
st.markdown(
    """
<style>

/* Info box text */
div[data-testid="stAlert"] {
    color: white !important;
}

/* Expander text */
details {
    color: white !important;
}

/* Markdown text inside expanders */
details p {
    color: white !important;
}

/* Streamlit info/success/warning text */
.stAlert p {
    color: white !important;
}

/* General paragraph text */
p {
    color: white !important;
}

</style>
""",
    unsafe_allow_html=True,
)
# =========================
# ANALYTICS MODE
# =========================
if "analytics_mode" not in st.session_state:
    st.session_state.analytics_mode = False
# =========================
# SESSION STATE DEFAULTS
# =========================
st.session_state.setdefault("streak", 0)
st.session_state.setdefault("last_visit", None)
st.session_state.setdefault("best_streak", 0)
st.session_state.setdefault("show_insights", False)

if "page" not in st.session_state:
    st.session_state.page = "Profile"
if "profile_history" not in st.session_state:
    st.session_state.profile_history = []
if "plan_history" not in st.session_state:
    st.session_state.plan_history = []
if "ai_memory" not in st.session_state:
    st.session_state.ai_memory = {
        "workout_history": [],
        "diet_history": [],
        "coach_history": [],
    }

# =========================
# HELPER FUNCTIONS
# =========================


def clean_html(text):
    return re.sub(r"<.*?>", "", str(text or "")).strip()


def make_pdf_bytes(text, title="Report"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    content = [Paragraph(f"<b>{title}</b>", styles["Heading2"])]
    for line in text.split("\n"):
        content.append(Paragraph(line, styles["Normal"]))
    doc.build(content)
    buffer.seek(0)
    return buffer


def update_memory(type_key, result):
    if "plan_history" not in st.session_state:
        st.session_state["plan_history"] = []
    history = st.session_state["plan_history"]
    if history and history[-1].get("content") == result:
        return
    history.append(
        {
            "type": type_key.replace("_history", "").capitalize(),
            "date": str(pd.Timestamp.today().date()),
            "content": result,
            "favorite": False,
        }
    )
    st.session_state["plan_history"] = history


def get_memory(type):
    return st.session_state.ai_memory.get(type, [])


def analyze_progress():
    history = st.session_state.get("profile_history", [])
    if len(history) < 2:
        return "no_data"
    df = pd.DataFrame(history)
    df["weight"] = pd.to_numeric(df["weight"], errors="coerce")
    df = df.dropna().sort_values("date")
    change = df["weight"].iloc[-1] - df["weight"].iloc[0]
    if change < -1:
        return "losing"
    elif -1 <= change <= 1:
        return "stuck"
    else:
        return "gaining"


def get_user_profile():
    return f"""
Age: {st.session_state.get('age_input')}
Gender: {st.session_state.get('gender_input')}
Condition: {st.session_state.get('condition_input')}
Height: {st.session_state.get('height_input')}
Weight: {st.session_state.get('weight_input')}
Goal: {st.session_state.get('goal_input')}
Level: {st.session_state.get('level_input')}
Lifestyle: {st.session_state.get('lifestyle_input')}
Sleep: {st.session_state.get('sleep_input')}
Injury: {st.session_state.get('injury_input')}
"""


def get_progress():
    return str(st.session_state.get("profile_history", []))


def detect_intent(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["workout", "exercise", "gym", "form", "sets", "reps"]):
        return "workout"
    if any(k in t for k in ["diet", "food", "meal", "recipe", "nutrition"]):
        return "nutrition"
    if any(k in t for k in ["stress", "sleep", "relax", "anxiety"]):
        return "wellness"
    return "general"


def extract_links(text):
    return re.findall(r"https?://[^\s]+", text)


MEMORY_FILE = "coach_memory.json"


def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []


def save_memory(mem):
    with open(MEMORY_FILE, "w") as f:
        json.dump(mem, f)


# =========================
# GLOBAL HEADER
# =========================
col1, col2 = st.columns([8, 1])

with col1:
    st.markdown(
        """
<div style="margin-top:-10px;">
    <h1 style="margin-bottom:4px; font-size:28px;">⚡ AIVioMate</h1>
    <p style="margin-top:0; font-size:16px; opacity:0.8;">Train smart. Eat better. Live stronger.</p>
</div>
""",
        unsafe_allow_html=True,
    )

with col2:
    pass

st.markdown("---")
# =========================
# SESSION STATE DEFAULTS
# =========================

if "profile_data" not in st.session_state:
    st.session_state["profile_data"] = {}

if "progress_data" not in st.session_state:
    st.session_state["progress_data"] = {}

if "water" not in st.session_state:
    st.session_state["water"] = 0

if "sleep" not in st.session_state:
    st.session_state["sleep"] = 0

if "stress" not in st.session_state:
    st.session_state["stress"] = 0

if "energy" not in st.session_state:
    st.session_state["energy"] = 0

if "mood" not in st.session_state:
    st.session_state["mood"] = 0

if "analytics_data" not in st.session_state:
    st.session_state["analytics_data"] = []

# =========================
# NAVIGATION TABS
# =========================
tabs = [
    "Profile",
    "Dashboard",
    "Workout",
    "Nutrition",
    "Coach",
    "Wellness",
]
cols = st.columns(len(tabs))

for i, tab in enumerate(tabs):
    is_active = st.session_state.page == tab

    if cols[i].button(tab, key=f"tab_{tab}", use_container_width=True):
        st.session_state.page = tab
        st.rerun()

    if is_active:
        st.markdown(
            f"""
        <style>
        button[data-key="tab_{tab}"] {{
            background: linear-gradient(90deg, #6366f1, #8b5cf6) !important;
            color: white !important;
            box-shadow: 0 0 20px rgba(139,92,246,0.8);
            border: 1px solid #8b5cf6;
        }}
        </style>
        """,
            unsafe_allow_html=True,
        )

page = st.session_state.page

# =========================
# GLOBAL BACK BUTTON
# =========================
if page != "Profile":
    if st.button("⬅️ Back to Profile", key="back_btn"):
        st.session_state.page = "Profile"
        st.rerun()

st.markdown("---")

# =========================
# INSIGHTS FULL VIEW
# =========================
if st.session_state.get("show_insights"):

    st.markdown("## 📊 Detailed Insights")

    logs = st.session_state.get("daily_logs", [])

    if not logs:
        st.warning("⚠️ Start logging your daily data from Dashboard.")
    else:
        df = pd.DataFrame(logs)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        df["weight"] = pd.to_numeric(df["weight"], errors="coerce")
        df = df.dropna()

        target_weight = st.session_state.get("target_weight_input")

        try:
            target_weight = float(target_weight)
        except Exception:
            target_weight = None

        if len(df) >= 2:
            x = np.arange(len(df))
            y = df["weight"].values

            coef = np.polyfit(x, y, 1)
            trend = np.poly1d(coef)
            df["trend"] = trend(x)

            base = alt.Chart(df).encode(x="date:T")
            actual = base.mark_line(point=True).encode(
                y=alt.Y("weight:Q", title="Weight")
            )
            trend_line = base.mark_line(strokeDash=[5, 5]).encode(y="trend:Q")
            chart = actual + trend_line

            if target_weight:
                goal_line = (
                    alt.Chart(pd.DataFrame({"y": [target_weight]}))
                    .mark_rule(color="green")
                    .encode(y="y:Q")
                )
                chart += goal_line

            st.altair_chart(chart, use_container_width=True)

            if target_weight and coef[0] != 0:
                current_weight = y[-1]
                days_needed = (target_weight - current_weight) / coef[0]
                if days_needed > 0:
                    st.success(f"🎯 Target in ~{int(abs(days_needed))} days")

            avg_sleep = df["sleep"].mean()
            avg_water = df["water"].mean()

            insight = ""
            if avg_sleep < 6:
                insight += "😴 Improve sleep. "
            if avg_water < 5:
                insight += "💧 Increase hydration. "
            if coef[0] > 0:
                insight += "⚠️ Weight increasing."
            else:
                insight += "✅ On track."

            st.markdown(f"### 🧠 Insight\n{insight}")

        st.markdown("### 😴 Sleep Trend")
        st.line_chart(df.set_index("date")["sleep"])

        st.markdown("### 💧 Hydration Trend")
        st.line_chart(df.set_index("date")["water"])

        st.markdown("### 🌿 Wellness Score")
        st.line_chart(df.set_index("date")["score"])

    st.stop()


# =========================
# PROFILE PAGE
# =========================
if page == "Profile":

    st.markdown(
        """
<div style="
    background: rgba(255,255,255,0.05);
    padding:16px;
    border-radius:12px;
    color:white;
    font-size:17px;
    font-weight:500;
">
🚀 Welcome to your AI-powered wellness companion.<br><br>

""",
        unsafe_allow_html=True,
    )

    # =========================
    # HOW TO USE APP
    # =========================
    with st.expander("✨ How To Use The App", expanded=False):

        st.markdown(
            """
<style>
details summary {
    color: white !important;
    font-size: 20px !important;
    font-weight: 600 !important;
}
</style>
""",
            unsafe_allow_html=True,
        )

        st.markdown("""
### 👤 Step 1 — Complete Your Profile
Fill:
- age
- weight
- fitness goal
- lifestyle
- activity level

This helps AI personalize all recommendations.

---

### 📊 Dashboard
Track your:
- sleep
- stress
- energy
- hydration
- emotional wellness

Your Wellness Score updates automatically.

### 📈 Progress Analytics
Track long-term trends for:
- sleep
- hydration
- mood
- stress
- weight
- wellness score

---

### 💪 Workout Page
Generate:
- AI workout plans
- recovery-focused workouts
- strength/fat-loss routines
- Zumba & fun workouts

---

### 🥗 Nutrition Page
Get:
- personalized meal plans
- cuisine-based diets
- skin-focused nutrition
- hydration guidance

---

### 🧘 Wellness Page
Access:
- stress relief tips
- eye-care guidance
- recovery support
- wellness recommendations

---

### 🤖 AI Coach
Ask questions anytime about:
- workouts
- nutrition
- fat loss
- recovery
- wellness
""")

    col1, col2 = st.columns([1.5, 1])

    with col1:

        st.write("Tell us about yourself to personalize your plans.")

        age = st.text_input(
            "Age",
            placeholder="Enter your age",
            key="age_input",
        )

        gender = st.selectbox(
            "Gender",
            ["Select", "Male", "Female", "Other"],
            key="gender_input",
        )

        if gender == "Female":

            try:
                age_val = int(age)
            except Exception:
                age_val = 0

            if age_val < 18:

                special_condition = "N/A"
                st.session_state["condition_input"] = "N/A"

                st.info("⚠️ Special conditions not applicable for this age")

            else:

                special_condition = st.selectbox(
                    "Special Condition",
                    ["None", "Pregnant", "Postpartum"],
                    key="condition_input",
                )

        else:

            special_condition = "N/A"
            st.session_state["condition_input"] = "N/A"

        height = st.text_input(
            "Height (cm)",
            placeholder="Enter your height",
            key="height_input",
        )

        weight = st.text_input(
            "Weight (kg)",
            placeholder="Enter your weight",
            key="weight_input",
        )

        target_weight = st.text_input(
            "Target Weight (kg)",
            key="target_weight_input",
        )

        if height and weight:

            try:

                h = float(height) / 100
                w = float(weight)

                bmi = round(w / (h**2), 2)

                if bmi < 18.5:
                    status = "Underweight ❗"
                    color = "red"

                elif bmi < 25:
                    status = "Normal ✅"
                    color = "green"

                else:
                    status = "Overweight ⚠️"
                    color = "red"

                ideal_min = round(18.5 * (h**2), 1)
                ideal_max = round(24.9 * (h**2), 1)

                st.markdown(
                    f"""
<div style="background: rgba(255,255,255,0.05); padding:12px; border-radius:10px;">
<b>BMI:</b> <span style="color:{color};">{bmi} ({status})</span><br>
🎯 Ideal Weight Range: {ideal_min} - {ideal_max} kg
</div>
""",
                    unsafe_allow_html=True,
                )

            except Exception:

                st.warning("Enter valid height and weight")

        goal = st.selectbox(
            "Goal",
            [
                "Select Goal",
                "Fat Loss",
                "Strength Training",
                "Muscle Gain",
                "Weight Gain",
                "General Fitness",
                "Running",
            ],
            key="goal_input",
        )

        level = st.selectbox(
            "Fitness Level",
            ["Select Level", "Beginner", "Intermediate", "Advanced"],
            key="level_input",
        )

        lifestyle = st.selectbox(
            "Lifestyle",
            [
                "Select Lifestyle",
                "Sedentary (desk job)",
                "Moderately Active",
                "Very Active",
            ],
            key="lifestyle_input",
        )

        sleep_pref = st.slider(
            "Average Sleep (hrs)",
            0,
            10,
            6,
            key="sleep_input",
        )

        injury = st.selectbox(
            "Injury",
            [
                "None",
                "Knee Pain",
                "Back Pain",
                "Ankle Pain",
                "Shoulder Pain",
            ],
            key="injury_input",
        )

        # =========================
        # SAVE PROFILE
        # =========================
        if st.button("💾 Save Profile"):

            if (
                not age
                or not height
                or not weight
                or goal == "Select Goal"
                or level == "Select Level"
                or lifestyle == "Select Lifestyle"
            ):

                st.warning("⚠️ Please fill all required fields")

            else:

                import datetime

                st.success("✅ Profile saved successfully!")

                st.session_state["profile_data"] = {
                    "age": age,
                    "gender": gender,
                    "condition": special_condition,
                    "height": height,
                    "weight": weight,
                    "target_weight": target_weight,
                    "goal": goal,
                    "level": level,
                    "lifestyle": lifestyle,
                    "sleep": sleep_pref,
                    "injury": injury,
                }

                if "profile_history" not in st.session_state:
                    st.session_state["profile_history"] = []

                st.session_state["profile_history"].append(
                    {
                        "date": datetime.datetime.now(),
                        "weight": weight,
                    }
                )

        # =========================
        # RESET PROFILE
        # =========================
        if st.button("Reset Profile"):

            # Current profile
            st.session_state["profile_data"] = {}
            st.session_state["progress_data"] = {}

            # Dashboard current values
            st.session_state["water"] = 0
            st.session_state["sleep"] = 0
            st.session_state["stress"] = 0
            st.session_state["energy"] = 0
            st.session_state["mood"] = 0
            st.success("✅ Profile reset successfully")

            st.rerun()

    with col2:
        pass


# =========================
# DASHBOARD PAGE
# =========================
elif page == "Dashboard":

    import pandas as pd
    import plotly.express as px
    import datetime
    import random

    # =========================
    # INIT STATES
    # =========================
    if "analytics_mode" not in st.session_state:
        st.session_state.analytics_mode = False

    if "water" not in st.session_state:
        st.session_state.water = 0

    if "mood" not in st.session_state:
        st.session_state.mood = 0

    if "checkin_started" not in st.session_state:
        st.session_state.checkin_started = False

    if "analytics_data" not in st.session_state:
        st.session_state.analytics_data = []

    # =========================================================
    # DASHBOARD MODE
    # =========================================================
    if not st.session_state.analytics_mode:

        col1, col2 = st.columns([1.8, 1])

        # =================================================
        # LEFT SIDE
        # =================================================
        with col1:

            st.markdown("## 🧠 Daily Check-in")
            st.caption("Track your wellness, mood, hydration & recovery daily.")
            st.markdown("<br>", unsafe_allow_html=True)

            # =========================
            # SLIDERS
            # =========================
            c1, c2 = st.columns(2)

            with c1:
                sleep = st.slider(
                    "Sleep (hrs)", 0, 10, st.session_state.get("sleep", 6)
                )

            with c2:
                stress = st.slider("Stress", 0, 10, st.session_state.get("stress", 4))

            energy = st.slider("Energy", 0, 10, st.session_state.get("energy", 6))

            st.session_state["sleep"] = sleep
            st.session_state["stress"] = stress
            st.session_state["energy"] = energy

            st.markdown("---")

            # =========================
            # EMOTIONAL HEALTH
            # =========================
            st.markdown("### 😊 Emotional Health")
            st.caption("How are you feeling today?")

            mood_map = {
                "😞": ("Low", 2),
                "😐": ("Okay", 5),
                "🙂": ("Good", 7),
                "😄": ("Great", 10),
            }

            mood_cols = st.columns(4)

            for i, (emoji, (label, value)) in enumerate(mood_map.items()):
                with mood_cols[i]:
                    if st.button(emoji, key=f"mood_{emoji}", use_container_width=True):
                        st.session_state.mood = value
                        st.session_state.mood_label = label
                        st.session_state.checkin_started = True
                        st.rerun()

            if "mood_label" in st.session_state:
                st.success(f"Current Mood: {st.session_state.mood_label}")

            mood = st.session_state.get("mood", 0)

            st.markdown("---")

            # =========================
            # HYDRATION
            # =========================
            st.markdown("### 💧 Hydration Tracker")

            water = st.session_state.water

            st.markdown(f"#### {water} / 8 glasses")

            st.progress(min(water / 8, 1.0))

            h1, h2, h3 = st.columns(3)

            with h1:
                if st.button("➕ Drink Water", use_container_width=True):
                    if st.session_state.water < 8:
                        st.session_state.water += 1
                    st.rerun()

            with h2:
                if st.button("➖ Remove Water", use_container_width=True):
                    if st.session_state.water > 0:
                        st.session_state.water -= 1
                    st.rerun()

            with h3:
                if st.button("🔄 Reset Water", use_container_width=True):
                    st.session_state.water = 0
                    st.rerun()

            # =========================
            # WELLNESS SCORE
            # =========================
            if sleep > 0 or stress > 0 or energy > 0 or mood > 0:
                st.session_state.checkin_started = True

            if st.session_state.checkin_started:

                hydration_score = min(water, 8) * 10

                score = int(
                    (
                        (sleep * 10)
                        + ((10 - stress) * 10)
                        + (energy * 10)
                        + (mood * 10)
                        + hydration_score
                    )
                    / 5
                )

                color = (
                    "#ef4444" if score < 40 else "#f59e0b" if score < 70 else "#22c55e"
                )
                label = (
                    "Needs Attention"
                    if score < 40
                    else "Good" if score < 70 else "Excellent"
                )

                st.markdown("---")
                st.markdown("## 🚀 Wellness Score")
                st.progress(score / 100)

                st.markdown(
                    f"""
<div style="
background: rgba(255,255,255,0.04);
padding:25px;
border-radius:16px;
text-align:center;
border:1px solid rgba(255,255,255,0.08);
">
    <h1 style="font-size:60px; margin-bottom:0; color:{color};">{score}</h1>
    <p style="font-size:20px; color:white;">{label}</p>
</div>
""",
                    unsafe_allow_html=True,
                )

            # =========================
            # SMART TIPS
            # =========================
            st.markdown("---")
            st.markdown("### 💡 Smart Lifestyle Tips")

            tips = []

            if sleep < 6:
                tips.append("😴 Sleep is low — aim for 7–8 hrs")
            if stress >= 7:
                tips.append("🧘 High stress detected — prioritize recovery")
            if energy < 5:
                tips.append("⚡ Low energy — improve sleep + hydration")
            if mood <= 5:
                tips.append("🙂 Mood seems slightly low — take a break")
            if water < 5:
                tips.append("💧 Increase water intake")
            if not tips:
                tips.append("🔥 Excellent consistency today")

            for tip in tips:
                st.markdown(f"- {tip}")

            # =========================
            # ANALYTICS BUTTON
            # =========================
            st.markdown("---")
            st.markdown("### 📊 Progress Analytics")

            if st.button("📈 Open Detailed Analytics", use_container_width=True):
                st.session_state.analytics_mode = True
                st.rerun()

            # =========================
            # RESET BUTTON
            # =========================
            if st.button("🔄 Reset Dashboard", use_container_width=True):
                st.session_state.water = 0
                st.session_state.mood = 0
                st.session_state.checkin_started = False
                st.rerun()

        # =================================================
        # RIGHT SIDE IMAGE
        # =================================================
        with col2:

            st.markdown("<br><br>", unsafe_allow_html=True)

            st.image(
                "https://images.unsplash.com/photo-1517836357463-d25dfeac3438",
                use_container_width=True,
            )

    # =========================================================
    # ANALYTICS MODE
    # =========================================================
    else:

        st.markdown("### 📊 Detailed Wellness Analytics")
        st.caption("Track your wellness trends and recovery patterns.")

        if st.button("⬅ Back to Dashboard"):
            st.session_state.analytics_mode = False
            st.rerun()

        st.markdown("---")

        # =====================================================
        # ALWAYS CREATE DUMMY DATA IF MISSING/BROKEN
        # =====================================================
        required_cols = [
            "date",
            "sleep",
            "stress",
            "energy",
            "water",
            "mood",
            "weight",
            "wellness_score",
        ]

        recreate_data = False

        if "analytics_data" not in st.session_state:
            recreate_data = True
        else:
            try:
                temp_df = pd.DataFrame(st.session_state.analytics_data)

                if temp_df.empty:
                    recreate_data = True
                elif not all(col in temp_df.columns for col in required_cols):
                    recreate_data = True

            except Exception:
                recreate_data = True

        # =====================================================
        # CREATE DUMMY ANALYTICS DATA
        # =====================================================
        if recreate_data:

            st.session_state.analytics_data = []
            base_date = datetime.datetime.now()

            for i in range(14):
                st.session_state.analytics_data.append(
                    {
                        "date": base_date - datetime.timedelta(days=13 - i),
                        "sleep": random.randint(5, 9),
                        "stress": random.randint(2, 8),
                        "energy": random.randint(4, 10),
                        "water": random.randint(3, 8),
                        "mood": random.randint(4, 10),
                        "weight": random.randint(58, 82),
                        "wellness_score": random.randint(55, 95),
                    }
                )

        # =====================================================
        # DATAFRAME
        # =====================================================
        df = pd.DataFrame(st.session_state.analytics_data)
        df["date"] = pd.to_datetime(df["date"])

        # =====================================================
        # CHARTS
        # =====================================================
        charts = [
            ("sleep", "😴 Sleep Trend"),
            ("stress", "🧘 Stress Trend"),
            ("energy", "⚡ Energy Trend"),
            ("water", "💧 Hydration Trend"),
            ("mood", "😊 Mood Trend"),
            ("weight", "⚖️ Weight Trend"),
            ("wellness_score", "🚀 Wellness Score"),
        ]

        for metric, title in charts:

            st.markdown(f"### {title}")

            fig = px.line(df, x="date", y=metric, markers=True)

            fig.update_layout(
                paper_bgcolor="#081028",
                plot_bgcolor="#111827",
                font=dict(color="white"),
                height=400,
                margin=dict(l=20, r=20, t=30, b=20),
            )

            st.plotly_chart(fig, use_container_width=True)

# =========================
# WORKOUT PAGE
# =========================
elif page == "Workout":

    col1, col2 = st.columns([1.5, 1])

    with col1:

        st.markdown("## 💪 Workout Plan")
        st.write("Train smarter. Build strength.")

        st.info("👉 Tip: Fill your Profile for better AI recommendations")

        # =========================
        # GENERATE WORKOUT
        # =========================
        if st.button("Generate AI Workout"):

            profile_data = st.session_state.get("profile_data", {})
            progress = st.session_state.get("progress_data", {})

            required_fields = ["age", "weight", "goal", "level"]

            missing = [
                field
                for field in required_fields
                if not profile_data.get(field)
                or str(profile_data.get(field)).startswith("Select")
            ]

            if missing:

                st.warning(
                    "⚠️ Complete your Profile page before generating workout plans."
                )

            else:

                result = generate_workout(profile_data, progress)

                st.session_state["workout_result"] = result

                update_memory("workout_history", result)

        # =========================
        # SHOW RESULT
        # =========================
        if "workout_result" in st.session_state:

            st.markdown("### 🏋️ Your Workout Plan")

            clean_text = re.sub(
                r"<.*?>",
                "",
                st.session_state["workout_result"],
            )

            buffer = BytesIO()

            doc = SimpleDocTemplate(buffer)

            styles = getSampleStyleSheet()

            content = []

            for line in clean_text.split("\n"):

                content.append(
                    Paragraph(
                        line,
                        styles["Normal"],
                    )
                )

            doc.build(content)

            buffer.seek(0)

            st.download_button(
                "📄 Download Workout Plan",
                buffer,
                file_name="workout_plan.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

            st.markdown("---")

            st.markdown(clean_text)

        # =========================
        # WORKOUT HISTORY
        # =========================
        st.markdown("---")

        st.markdown("## 📚 Workout History")

        history = st.session_state.get("plan_history", [])

        workouts = [h for h in history if h["type"].lower() == "workout"]

        if workouts:

            for item in reversed(workouts[-5:]):

                with st.expander(f"💪 {item['date']}"):

                    st.markdown(item["content"])

        else:

            st.info("No workout history yet.")

    with col2:

        st.image(
            "https://images.unsplash.com/photo-1599058917212-d750089bc07e",
            use_container_width=True,
        )

    st.markdown("---")

    # =========================
    # ZUMBA
    # =========================
    st.markdown(
        """
    <div style="
    background:#102044;
    padding:16px;
    border-radius:12px;
    color:white;
    font-size:18px;
    font-weight:500;
    ">
    💃 Want something fun? Try dance workouts
    </div>
    """,
        unsafe_allow_html=True,
    )

    if st.button("Show Zumba Workouts"):

        result = generate_zumba()

        st.markdown("### 💃 Zumba Plan")

        st.markdown(result)

# =========================
# NUTRITION PAGE
# =========================
elif page == "Nutrition":

    col1, col2 = st.columns([1.5, 1])

    with col1:

        st.markdown("## 🥗 Nutrition Plan")
        st.write("Fuel your body & skin the right way.")

        cuisine = st.selectbox(
            "Cuisine",
            [
                "Select Cuisine",
                "Indian",
                "South Indian",
                "North Indian",
                "Continental",
            ],
        )

        food_type = st.selectbox(
            "Food Type",
            [
                "Select Food Type",
                "Veg",
                "Non-Veg",
                "Vegan",
            ],
        )

        st.markdown("### ✨ Skin Preferences")

        skin_type = st.selectbox(
            "Skin Type",
            [
                "Select Skin Type",
                "Dry",
                "Sensitive",
                "Oily",
                "Combination",
                "Acne-prone",
            ],
        )

        skin_goal = st.selectbox(
            "Skin Goal",
            [
                "Select Skin Goal",
                "Acne Control",
                "Glow",
                "Anti-aging",
                "Pigmentation",
            ],
        )

        st.markdown("---")

        # =========================
        # GENERATE DIET
        # =========================
        if st.button("Generate Diet Plan"):

            profile_data = st.session_state.get("profile_data", {})
            progress = st.session_state.get("progress_data", {})

            required_fields = [
                "age",
                "weight",
                "goal",
                "level",
            ]

            missing = [
                field
                for field in required_fields
                if not profile_data.get(field)
                or str(profile_data.get(field)).startswith("Select")
            ]

            if missing:

                st.warning(
                    "⚠️ Please complete your Profile page before generating a personalized nutrition plan."
                )

            else:

                final_profile = {
                    **profile_data,
                    "cuisine": cuisine,
                    "food_type": food_type,
                    "skin_type": skin_type,
                    "skin_goal": skin_goal,
                }

                result = generate_diet(
                    final_profile,
                    progress,
                    cuisine,
                    food_type,
                    skin_type,
                    skin_goal,
                )

                st.session_state["diet_result"] = result
                update_memory("diet_history", result)

        # =========================
        # SHOW RESULT
        # =========================
        if "diet_result" in st.session_state:

            st.markdown("### 🍽️ Your Nutrition Plan")

            st.success("🥗 Personalized for your lifestyle + skin")
            st.caption("Your plan below may include personalized suggestions as well.")
            st.caption("💊 Supplements are general suggestions")

            clean_text = re.sub(
                r"<.*?>",
                "",
                st.session_state["diet_result"],
            )

            buffer = BytesIO()

            doc = SimpleDocTemplate(buffer)

            styles = getSampleStyleSheet()

            content = []

            for line in clean_text.split("\n"):

                content.append(
                    Paragraph(
                        line,
                        styles["Normal"],
                    )
                )

            doc.build(content)

            buffer.seek(0)

            st.download_button(
                "📄 Download Diet Plan",
                buffer,
                file_name="diet_plan.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

            st.markdown("---")

            st.markdown(clean_text)
            # =========================
        # NUTRITION HISTORY
        # =========================
        st.markdown("---")

        st.markdown("## 📚 Nutrition History")

        history = st.session_state.get("plan_history", [])

        diets = [h for h in history if h["type"].lower() == "diet"]

        if diets:

            for item in reversed(diets[-5:]):

                with st.expander(f"🥗 {item['date']}"):

                    st.markdown(item["content"])

        else:

            st.info("No nutrition history yet.")

    with col2:

        st.image(
            "https://libapps-au.s3-ap-southeast-2.amazonaws.com/accounts/97668/images/teadergrafik_nutritions.jpg",
            use_container_width=True,
        )


# =========================
# COACH PAGE
# =========================
elif page == "Coach":

    col1, col2 = st.columns([1.5, 1])

    with col1:

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        if "prefill" not in st.session_state:
            st.session_state.prefill = ""

        st.markdown("## 🤖 AI Wellness Coach")

        st.markdown("### 💡 Try asking:")

        suggestions = [
            "Give me a workout for fat loss",
            "Easy high-protein breakfast ideas",
            "How to reduce stress quickly",
        ]

        scols = st.columns(len(suggestions))

        for i, q in enumerate(suggestions):

            if scols[i].button(q):

                st.session_state.prefill = q

        st.markdown("---")

        # =========================
        # CHAT HISTORY
        # =========================
        for msg in st.session_state.chat_history:

            cls = "user-bubble" if msg["role"] == "user" else "bot-bubble"

            st.markdown(
                f'<div class="{cls}">{msg["content"]}</div>',
                unsafe_allow_html=True,
            )

        user_input = st.text_input(
            "Ask your coach...",
            value=st.session_state.prefill,
            key="coach_input",
        )

        if st.button("Get Guidance") and user_input:

            st.session_state.chat_history.append(
                {
                    "role": "user",
                    "content": user_input,
                }
            )

            profile = get_user_profile()

            reply = coach_reply(
                user_input,
                profile,
            )

            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": reply,
                }
            )

            st.session_state.prefill = ""

            st.rerun()

        # =========================
        # COACH MEMORY
        # =========================
        st.markdown("---")

        st.markdown("## 📚 Recent Conversations")

        if st.session_state.chat_history:

            recent = st.session_state.chat_history[-6:]

            for msg in recent:

                role = "🧑 You" if msg["role"] == "user" else "🤖 Coach"

                with st.expander(role):

                    st.markdown(msg["content"])

        else:

            st.info("No conversations yet.")

    with col2:

        st.image(
            "https://coachvox.ai/wp-content/uploads/2023/04/AI-enhanced-coaching.jpg",
            use_container_width=True,
        )

# =========================
# WELLNESS PAGE
# =========================
elif page == "Wellness":

    st.caption("Focus on recovery, relaxation and overall well-being.")

    tab1, tab2, tab3 = st.tabs(["🧘 Stress", "👁️ Eye Care", "💊 Support"])

    # =========================
    # STRESS TAB
    # =========================
    with tab1:

        col1, col2 = st.columns([1.5, 1])

        with col1:
            st.markdown("### 🧘 Stress Relief")

            if st.button("Get Relaxation Plan"):
                profile = st.session_state.get("profile_data", "No profile")

                result = stress_relief(profile)

                st.session_state["stress_result"] = result

            if "stress_result" in st.session_state:
                st.markdown(st.session_state["stress_result"])

        with col2:
            st.image(
                "https://images.unsplash.com/photo-1506126613408-eca07ce68773",
                use_container_width=True,
            )

    # =========================
    # EYE CARE TAB
    # =========================
    with tab2:

        col1, col2 = st.columns([1.5, 1])

        with col1:
            st.markdown("## 👁️ Eye Care")

            st.markdown("""
### 💡 Daily Eye Care Tips

• Follow **20-20-20 rule**  
• Blink frequently  
• Reduce screen brightness  
• Use proper lighting  
• Sleep 7–8 hours  
""")

            if st.button("Get Personalized Eye Tips"):
                profile = st.session_state.get("profile_data", {})

                result = generate_eye_care(profile)

                st.session_state["eye_tips"] = result

            if "eye_tips" in st.session_state:
                st.success("👁️ Personalized eye-care recommendations generated")
                st.markdown(st.session_state["eye_tips"])

        with col2:
            st.image(
                "https://images.unsplash.com/photo-1516321318423-f06f85e504b3",
                use_container_width=True,
            )

    # =========================
    # SUPPORT TAB
    # =========================
    with tab3:

        col1, col2 = st.columns([1.5, 1])

        with col1:
            st.markdown("### 💊 General Wellness Support")
            st.caption("Non-medical suggestions")

            st.markdown("""
- Magnesium → helps relaxation  
- Herbal tea → supports stress relief  
- Electrolytes → supports hydration  
- Vitamin B12 → supports energy  
- Omega-3 → supports brain health  
""")

            st.caption("⚠️ Always consult a professional before supplements")

        with col2:
            st.image(
                "https://images.unsplash.com/photo-1498837167922-ddd27525d352",
                use_container_width=True,
            )


# =========================
# ANALYTICS PAGE
# =========================
elif page == "📊 Analytics":

    st.markdown("## 📊 Analytics")

    logs = st.session_state.get("daily_logs", [])

    if not logs:
        st.warning("⚠️ No daily data yet. Start logging from the Dashboard.")
    else:
        df = pd.DataFrame(logs)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")

        sleep = st.session_state.get("sleep", 0)
        stress = st.session_state.get("stress", 0)
        energy = st.session_state.get("energy", 0)
        water = st.session_state.get("water", 0)

        st.markdown("---")

        # =========================
        # ACTION CENTER
        # =========================
        st.markdown("## 🎯 Recommended Actions")

        actions = []

        if sleep < 6:
            actions.append("🛌 Improve sleep schedule")

        if stress > 7:
            actions.append("🧘 Try stress-relief exercises")

        if water < 5:
            actions.append("💧 Increase hydration")

        if energy < 5:
            actions.append("⚡ Prioritize nutrition + recovery")

        if actions:
            for action in actions:
                st.markdown(f"- {action}")
        else:
            st.success("🔥 Keep following your current routine")

        st.markdown("---")

        # =========================
        # PROGRESS HISTORY TABLE
        # =========================
        st.markdown("## 📋 Daily History")

        st.dataframe(
            df,
            use_container_width=True,
        )
