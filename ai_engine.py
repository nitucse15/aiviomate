# =========================
# 🤖 AI ENGINE (FINAL CLEAN VERSION)
# =========================

from openai import OpenAI
import os

# ✅ Uses environment variable (correct way)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =========================
# 💪 WORKOUT
# =========================
def generate_workout(profile, progress):


    prompt = f"""
You are an elite fitness coach and recovery specialist.

Create a STRICTLY personalized 7-day workout plan.

USER PROFILE:
{profile}

PROGRESS DATA:
{progress}

IMPORTANT RULES:

1. RUNNING GOAL:
- Include:
    • Easy Run
    • Interval Run
    • Long Run
- Include 2 strength days for runners
- Include mobility + recovery
- Avoid excessive bodybuilding workouts

2. FAT LOSS GOAL:
- Mix strength + cardio
- Higher calorie burn
- Moderate intensity
- Add recovery day

3. MUSCLE GAIN / STRENGTH:
- Focus resistance training
- Progressive overload
- Split muscle groups
- Less cardio

4. WEIGHT GAIN:
- Avoid excessive cardio
- Focus hypertrophy + recovery

5. GENERAL FITNESS:
- Balanced workouts
- Functional movement
- Mobility + conditioning

6. BEGINNER:
- Simple exercises
- Lower intensity
- More recovery

7. ADVANCED:
- Higher intensity
- Complex movements

8. PREGNANT:
- NO jumping
- NO HIIT
- NO risky core exercises
- Include walking, mobility, breathing

9. POSTPARTUM:
- Focus pelvic floor
- Core recovery
- Low-impact workouts
- Gradual progression

10. INJURIES:
- Avoid aggravating movements

FORMAT:
Day 1:
- Warm-up
- Main Workout
- Duration
- Intensity
- Cool-down

IMPORTANT:
The plan MUST clearly align with the user's exact goal.
Do NOT generate generic workouts.
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content


# =========================
# 🥗 DIET (UPDATED)
# =========================
def generate_diet(profile, progress, cuisine, food_type, skin_type, skin_goal):

    prompt = f"""
You are an expert sports nutritionist and wellness coach.

Create a STRICT personalized 7-day diet plan.

USER PROFILE:
{profile}

PROGRESS:
{progress}

CUISINE:
{cuisine}

FOOD TYPE:
{food_type}

SKIN TYPE:
{skin_type}

SKIN GOAL:
{skin_goal}

IMPORTANT RULES:

1. FAT LOSS:
- High protein
- Moderate calorie deficit
- Avoid excessive sugar

2. MUSCLE GAIN:
- High protein
- Higher calories
- Recovery-focused meals

3. RUNNING:
- Complex carbs
- Hydration
- Electrolytes
- Pre/post run meals

4. WEIGHT GAIN:
- Calorie surplus
- Nutrient-dense foods

5. PREGNANT:
- Iron
- Calcium
- Folate-rich foods
- Avoid unsafe foods

6. POSTPARTUM:
- Recovery foods
- Hydration
- Protein
- Iron-rich meals

7. ACNE / OILY SKIN:
- Lower processed sugar
- Anti-inflammatory foods

8. DRY SKIN:
- Healthy fats
- Hydration-rich foods

9. GLOW GOAL:
- Antioxidants
- Fruits
- Hydration

INCLUDE:
- Morning drink
- Breakfast
- Mid snack
- Lunch
- Evening snack
- Dinner
- Timing
- Portions
- Hydration

ALSO INCLUDE:
- Foods to avoid
- Skin-friendly foods
- Recovery recommendations

The output MUST feel personalized to the user's profile.
Do NOT generate generic diet plans.
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content


# =========================
# 🧠 COACH
# =========================
def coach_reply(question, profile):

    prompt = f"""
User Profile:
{profile}

Question:
{question}

Give smart, practical fitness advice.
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content


# =========================
# 🧘 STRESS RELIEF
# =========================
def stress_relief(profile):

    prompt = f"""
User Profile:
{profile}

Give stress relief suggestions including:
- Meditation
- Fun activities
- Music
- Relaxation ideas
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content


# =========================
# 💃 ZUMBA (UPDATED ✅)
# =========================
def generate_zumba():

    prompt = """
Give 3 Zumba YouTube video links with titles.

Format:
1. Title - https://youtube.com/...
2. Title - https://youtube.com/...
3. Title - https://youtube.com/...
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content


# ---------- EYE CARE ----------
def generate_eye_care(profile):

    prompt = f"""
Give personalized eye care tips.

User Profile:
{profile}

Include:
- Screen-time protection
- Eye relaxation
- Sleep advice
- Hydration
- Eye exercises
- Workplace eye care

DO NOT include:
- Workout advice
- Fat loss advice
- Gym recommendations
- Nutrition plans

Keep it practical and concise.
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ]
    )

    return res.choices[0].message.content