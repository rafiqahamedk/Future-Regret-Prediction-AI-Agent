"""
Module 1 — user_input.py
Validates and structures raw user input into a clean data dict
consumed by all downstream modules.
"""

from dataclasses import dataclass, asdict, field
from typing import Optional


@dataclass
class BasicInfo:
    name: str
    age: int
    career_goal: str


@dataclass
class DailyRoutine:
    study_hours: float = 0.0
    screen_time: float = 0.0
    sleep_hours: float = 7.0
    skill_learning_hours: float = 0.0
    exercise_hours: float = 0.0
    distraction_hours: float = 0.0


@dataclass
class WeeklyProductivity:
    projects_building: int = 0
    courses_learning: int = 0
    consistency_level: int = 5      # 1‑10
    focus_level: int = 5            # 1‑10


@dataclass
class SelfReflection:
    doing_well: str = ""
    avoiding: str = ""
    biggest_distraction: str = ""
    biggest_goal: str = ""


@dataclass
class UserProfile:
    basic: BasicInfo
    daily: DailyRoutine
    weekly: WeeklyProductivity
    reflection: SelfReflection

    def to_dict(self) -> dict:
        return {
            "basic":      asdict(self.basic),
            "daily":      asdict(self.daily),
            "weekly":     asdict(self.weekly),
            "reflection": asdict(self.reflection),
        }

    @staticmethod
    def from_dict(d: dict) -> "UserProfile":
        return UserProfile(
            basic=BasicInfo(**d["basic"]),
            daily=DailyRoutine(**d["daily"]),
            weekly=WeeklyProductivity(**d["weekly"]),
            reflection=SelfReflection(**d["reflection"]),
        )


# ── Validation helpers ──────────────────────────────────────

def validate_range(value, lo, hi, name: str):
    if not (lo <= value <= hi):
        raise ValueError(f"{name} must be between {lo} and {hi}, got {value}")
    return value


def build_profile(
    name: str, age: int, career_goal: str,
    study_hours: float, screen_time: float, sleep_hours: float,
    skill_learning_hours: float, exercise_hours: float, distraction_hours: float,
    projects_building: int, courses_learning: int,
    consistency_level: int, focus_level: int,
    doing_well: str = "", avoiding: str = "",
    biggest_distraction: str = "", biggest_goal: str = "",
) -> UserProfile:
    """Construct and validate a UserProfile from raw values."""

    validate_range(age, 10, 100, "Age")
    validate_range(study_hours, 0, 24, "Study hours")
    validate_range(screen_time, 0, 24, "Screen time")
    validate_range(sleep_hours, 0, 24, "Sleep hours")
    validate_range(skill_learning_hours, 0, 24, "Skill learning hours")
    validate_range(exercise_hours, 0, 24, "Exercise hours")
    validate_range(distraction_hours, 0, 24, "Distraction hours")
    validate_range(consistency_level, 1, 10, "Consistency level")
    validate_range(focus_level, 1, 10, "Focus level")

    return UserProfile(
        basic=BasicInfo(name=name.strip(), age=age, career_goal=career_goal),
        daily=DailyRoutine(
            study_hours=study_hours,
            screen_time=screen_time,
            sleep_hours=sleep_hours,
            skill_learning_hours=skill_learning_hours,
            exercise_hours=exercise_hours,
            distraction_hours=distraction_hours,
        ),
        weekly=WeeklyProductivity(
            projects_building=projects_building,
            courses_learning=courses_learning,
            consistency_level=consistency_level,
            focus_level=focus_level,
        ),
        reflection=SelfReflection(
            doing_well=doing_well.strip(),
            avoiding=avoiding.strip(),
            biggest_distraction=biggest_distraction.strip(),
            biggest_goal=biggest_goal.strip(),
        ),
    )
