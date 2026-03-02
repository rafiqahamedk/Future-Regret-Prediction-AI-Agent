"""
Module 5 — recommendation.py
Generates corrective action plans: things to STOP, things to START,
a weekly improvement plan, and daily habit changes.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict
from analyzer import AnalysisResult, GapItem
from regret_engine import RegretResult
from user_input import UserProfile
from config import CAREER_BENCHMARKS


@dataclass
class ActionItem:
    action: str
    priority: str        # HIGH / MEDIUM / LOW
    category: str        # Career, Skill, Health …
    impact: str          # short explanation


@dataclass
class Recommendation:
    stop_doing:   List[ActionItem] = field(default_factory=list)
    start_doing:  List[ActionItem] = field(default_factory=list)
    weekly_plan:  List[str] = field(default_factory=list)
    daily_habits: List[str] = field(default_factory=list)
    motivational: str = ""

    def to_dict(self) -> dict:
        return {
            "stop_doing":   [asdict(a) for a in self.stop_doing],
            "start_doing":  [asdict(a) for a in self.start_doing],
            "weekly_plan":  self.weekly_plan,
            "daily_habits": self.daily_habits,
            "motivational": self.motivational,
        }


# ── Internal rule helpers ───────────────────────────────────

def _stop_rules(profile: UserProfile, analysis: AnalysisResult) -> List[ActionItem]:
    items: List[ActionItem] = []
    d = profile.daily

    if d.distraction_hours > 2:
        items.append(ActionItem(
            action=f"Reduce social media / gaming from {d.distraction_hours:.1f} hrs to under 1 hr/day",
            priority="HIGH", category="Time Waste Regret",
            impact="Frees up hours for skill building and deep work",
        ))
    elif d.distraction_hours > 1:
        items.append(ActionItem(
            action=f"Cut distraction time from {d.distraction_hours:.1f} hrs to under 1 hr/day",
            priority="MEDIUM", category="Time Waste Regret",
            impact="Even 30 min saved daily = 180 hrs/year of extra learning",
        ))

    if d.screen_time > 5:
        items.append(ActionItem(
            action=f"Reduce total screen time from {d.screen_time:.1f} hrs — set app timers",
            priority="HIGH", category="Time Waste Regret",
            impact="Excessive screen time drains focus and worsens sleep",
        ))

    if d.sleep_hours < 6:
        items.append(ActionItem(
            action="Stop sacrificing sleep — 6 hrs minimum, 7‑8 recommended",
            priority="HIGH", category="Health Regret",
            impact="Sleep deprivation reduces cognitive performance by up to 40%",
        ))

    # Low‑value multitasking
    if profile.weekly.focus_level < 5:
        items.append(ActionItem(
            action="Stop multitasking during study / work blocks",
            priority="MEDIUM", category="Career Regret",
            impact="Single‑tasking boosts productivity by 20‑40%",
        ))

    return items


def _start_rules(profile: UserProfile, analysis: AnalysisResult) -> List[ActionItem]:
    items: List[ActionItem] = []
    d = profile.daily
    w = profile.weekly
    bench = CAREER_BENCHMARKS.get(profile.basic.career_goal,
                                  CAREER_BENCHMARKS["Other"])

    if d.study_hours < bench["study_hours"]:
        diff = bench["study_hours"] - d.study_hours
        items.append(ActionItem(
            action=f"Add {diff:.1f} hrs of focused study per day",
            priority="HIGH", category="Career Regret",
            impact=f"Needed to meet {profile.basic.career_goal} benchmarks",
        ))

    if d.skill_learning_hours < bench["skill_learning_hours"]:
        diff = bench["skill_learning_hours"] - d.skill_learning_hours
        items.append(ActionItem(
            action=f"Dedicate {diff:.1f} more hrs/day to hands‑on skill practice",
            priority="HIGH", category="Skill Regret",
            impact="Practical skill gaps are the #1 regret in career prep",
        ))

    if w.projects_building < max(1, bench["projects_per_week"]):
        items.append(ActionItem(
            action="Start building at least 1 project per month (ideally per week)",
            priority="HIGH", category="Career Regret",
            impact="Projects are proof of ability — resumes without them get filtered",
        ))

    if d.exercise_hours < bench["exercise_hours"]:
        items.append(ActionItem(
            action="Start a daily 30‑minute exercise routine (walk, gym, yoga)",
            priority="MEDIUM", category="Health Regret",
            impact="Exercise improves focus, mood, and long‑term health",
        ))

    if w.consistency_level < 6:
        items.append(ActionItem(
            action="Use a habit tracker and commit to 5+ consistent days/week",
            priority="HIGH", category="Career Regret",
            impact="Consistency beats intensity — small daily effort beats weekend cramming",
        ))

    if w.courses_learning < 1:
        items.append(ActionItem(
            action="Enroll in at least one structured course relevant to your goal",
            priority="MEDIUM", category="Skill Regret",
            impact="Guided learning accelerates skill acquisition",
        ))

    return items


def _weekly_plan(profile: UserProfile, analysis: AnalysisResult) -> List[str]:
    plan: List[str] = []
    bench = CAREER_BENCHMARKS.get(profile.basic.career_goal,
                                  CAREER_BENCHMARKS["Other"])
    study_target = max(profile.daily.study_hours, bench["study_hours"])
    skill_target = max(profile.daily.skill_learning_hours, bench["skill_learning_hours"])

    plan.append(f"Mon‑Fri: {study_target:.0f} hrs focused study + {skill_target:.0f} hrs skill practice")
    plan.append("Sat: Project work / portfolio building (2‑3 hrs)")
    plan.append("Sun: Review week, plan next week, rest & light reading")

    if profile.daily.exercise_hours < 0.5:
        plan.append("Daily: 30 min exercise (morning preferred)")

    if profile.daily.distraction_hours > 1:
        plan.append(f"Daily: Cap social media/gaming at 1 hr (currently {profile.daily.distraction_hours:.1f} hrs)")

    plan.append("Weekly: Track progress in a journal or app — review every Sunday")

    return plan


def _daily_habits(profile: UserProfile) -> List[str]:
    habits = [
        "Wake up at a consistent time every day",
        "First 2 hours: Deep work (no phone)",
        "Use Pomodoro (25 min focus / 5 min break)",
        "Review goals before bed (5 min)",
    ]
    if profile.daily.sleep_hours < 7:
        habits.append("Set a hard bedtime to get 7+ hrs of sleep")
    if profile.daily.distraction_hours > 1.5:
        habits.append("Delete / uninstall time‑wasting apps during weekdays")
    if profile.weekly.focus_level < 5:
        habits.append("Practice single‑tasking: one thing at a time")
    return habits


def _motivational(regret: RegretResult, profile: UserProfile) -> str:
    score = regret.overall_score
    name = profile.basic.name.split()[0] if profile.basic.name else "there"
    goal = profile.basic.career_goal

    if score <= 30:
        return (f"Great work, {name}! Your habits are well‑aligned with your "
                f"{goal} goal. Stay consistent and you'll be in an excellent position.")
    if score <= 55:
        return (f"{name}, you have a solid foundation but some gaps are forming. "
                f"Small adjustments now will pay huge dividends for your {goal} journey.")
    if score <= 75:
        return (f"{name}, this is a wake‑up call. Your current routine has noticeable "
                f"misalignments with your {goal} goal. The good news? Every change you "
                f"make today compounds. Start now.")
    return (f"{name}, your future self is counting on you to act TODAY. "
            f"The gap between where you are and your {goal} goal is widening fast. "
            f"Commit to one change right now — momentum will follow.")


# ── Public API ──────────────────────────────────────────────

def recommend(profile: UserProfile, analysis: AnalysisResult,
              regret: RegretResult) -> Recommendation:
    return Recommendation(
        stop_doing=_stop_rules(profile, analysis),
        start_doing=_start_rules(profile, analysis),
        weekly_plan=_weekly_plan(profile, analysis),
        daily_habits=_daily_habits(profile),
        motivational=_motivational(regret, profile),
    )
