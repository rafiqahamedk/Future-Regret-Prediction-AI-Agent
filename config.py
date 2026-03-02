"""
Configuration constants for the Future Regret Prediction AI Agent.
"""

# ── Database ────────────────────────────────────────────────
DB_PATH = "regret_agent.db"

# ── Scoring Weights (sum to 1.0) ────────────────────────────
WEIGHTS = {
    "consistency":    0.20,
    "productivity":   0.20,
    "distraction":    0.20,
    "goal_alignment": 0.25,
    "learning_effort":0.15,
}

# ── Thresholds ──────────────────────────────────────────────
REGRET_THRESHOLDS = {
    "LOW":      (0, 30),
    "MODERATE": (31, 55),
    "HIGH":     (56, 75),
    "CRITICAL": (76, 100),
}

# ── Career‑specific ideal benchmarks (per day, in hours) ───
CAREER_BENCHMARKS = {
    "Software Engineer": {
        "study_hours": 3,
        "coding_hours": 3,
        "skill_learning_hours": 2,
        "exercise_hours": 0.5,
        "max_screen_time": 3,
        "max_distraction": 1,
        "min_sleep": 7,
        "projects_per_week": 0.5,
        "courses_per_week": 1,
    },
    "AI/ML Engineer": {
        "study_hours": 4,
        "coding_hours": 3,
        "skill_learning_hours": 2.5,
        "exercise_hours": 0.5,
        "max_screen_time": 3,
        "max_distraction": 1,
        "min_sleep": 7,
        "projects_per_week": 0.5,
        "courses_per_week": 1,
    },
    "Data Scientist": {
        "study_hours": 3.5,
        "coding_hours": 2.5,
        "skill_learning_hours": 2,
        "exercise_hours": 0.5,
        "max_screen_time": 3,
        "max_distraction": 1,
        "min_sleep": 7,
        "projects_per_week": 0.5,
        "courses_per_week": 1,
    },
    "Government Job": {
        "study_hours": 6,
        "coding_hours": 0,
        "skill_learning_hours": 1,
        "exercise_hours": 0.5,
        "max_screen_time": 2,
        "max_distraction": 1,
        "min_sleep": 7,
        "projects_per_week": 0,
        "courses_per_week": 0.5,
    },
    "Business / Startup": {
        "study_hours": 2,
        "coding_hours": 1,
        "skill_learning_hours": 2,
        "exercise_hours": 0.5,
        "max_screen_time": 3,
        "max_distraction": 1.5,
        "min_sleep": 7,
        "projects_per_week": 1,
        "courses_per_week": 0.5,
    },
    "Freelancer": {
        "study_hours": 2,
        "coding_hours": 3,
        "skill_learning_hours": 2,
        "exercise_hours": 0.5,
        "max_screen_time": 3,
        "max_distraction": 1,
        "min_sleep": 7,
        "projects_per_week": 1,
        "courses_per_week": 0.5,
    },
    "Other": {
        "study_hours": 2,
        "coding_hours": 1,
        "skill_learning_hours": 1.5,
        "exercise_hours": 0.5,
        "max_screen_time": 3,
        "max_distraction": 1.5,
        "min_sleep": 7,
        "projects_per_week": 0.25,
        "courses_per_week": 0.5,
    },
}

CAREER_OPTIONS = list(CAREER_BENCHMARKS.keys())

# ── Time‑horizon labels ────────────────────────────────────
TIME_HORIZONS = {
    "3_months":  "3 months",
    "6_months":  "6 months",
    "1_year":    "1 year",
    "2_years":   "2 years",
}

# ── Regret types ────────────────────────────────────────────
REGRET_TYPES = [
    "Career Regret",
    "Skill Regret",
    "Time Waste Regret",
    "Health Regret",
    "Financial Regret",
]
