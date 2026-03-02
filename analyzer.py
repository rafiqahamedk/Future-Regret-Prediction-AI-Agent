"""
Module 2 — analyzer.py
Compares user habits against career‑specific benchmarks and
produces a structured gap analysis used by the regret engine.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List
from user_input import UserProfile
from config import CAREER_BENCHMARKS


@dataclass
class GapItem:
    metric: str
    current: float
    ideal: float
    gap: float            # positive = shortfall, negative = surplus
    severity: str         # LOW / MODERATE / HIGH / CRITICAL
    category: str         # maps to a regret type


@dataclass
class AnalysisResult:
    gaps: List[GapItem] = field(default_factory=list)
    sub_scores: Dict[str, float] = field(default_factory=dict)
    # sub_scores keys: consistency, productivity, distraction,
    #                  goal_alignment, learning_effort

    def to_dict(self) -> dict:
        return {
            "gaps": [asdict(g) for g in self.gaps],
            "sub_scores": self.sub_scores,
        }


# ── Severity helpers ────────────────────────────────────────

def _severity(ratio: float) -> str:
    """Map a 0‑1 gap ratio to severity label."""
    if ratio <= 0.2:
        return "LOW"
    if ratio <= 0.45:
        return "MODERATE"
    if ratio <= 0.7:
        return "HIGH"
    return "CRITICAL"


# ── Core analysis ───────────────────────────────────────────

def analyze(profile: UserProfile) -> AnalysisResult:
    """Run a full gap analysis and return sub‑scores."""

    career = profile.basic.career_goal
    bench  = CAREER_BENCHMARKS.get(career, CAREER_BENCHMARKS["Other"])
    daily  = profile.daily
    weekly = profile.weekly
    result = AnalysisResult()

    # ---- helper: compute gap for "more is better" metrics ----
    def _gap_more(metric, current, ideal, category):
        if ideal == 0:
            return 0.0
        shortfall = max(0, ideal - current) / ideal  # 0‑1
        result.gaps.append(GapItem(
            metric=metric, current=current, ideal=ideal,
            gap=round(ideal - current, 2),
            severity=_severity(shortfall),
            category=category,
        ))
        return shortfall

    # ---- helper: compute gap for "less is better" metrics ----
    def _gap_less(metric, current, ideal_max, category):
        if ideal_max == 0:
            ideal_max = 0.5
        excess = max(0, current - ideal_max) / ideal_max  # 0‑…
        excess = min(excess, 1.0)
        result.gaps.append(GapItem(
            metric=metric, current=current, ideal=ideal_max,
            gap=round(current - ideal_max, 2),
            severity=_severity(excess),
            category=category,
        ))
        return excess

    # ── 1. Goal alignment score ─────────────────────────────
    ga_gaps = []
    ga_gaps.append(_gap_more("Study hours/day", daily.study_hours,
                             bench["study_hours"], "Career Regret"))
    if bench["coding_hours"] > 0:
        ga_gaps.append(_gap_more("Coding/skill practice hours/day",
                                 daily.skill_learning_hours,
                                 bench["coding_hours"], "Skill Regret"))
    goal_alignment = 1 - (sum(ga_gaps) / max(len(ga_gaps), 1))
    goal_alignment = max(0, min(1, goal_alignment))

    # ── 2. Learning effort score ────────────────────────────
    le_gaps = []
    le_gaps.append(_gap_more("Skill learning hours/day",
                             daily.skill_learning_hours,
                             bench["skill_learning_hours"], "Skill Regret"))
    le_gaps.append(_gap_more("Courses/week", weekly.courses_learning,
                             bench["courses_per_week"], "Skill Regret"))
    le_gaps.append(_gap_more("Projects/week", weekly.projects_building,
                             bench["projects_per_week"], "Career Regret"))
    learning_effort = 1 - (sum(le_gaps) / max(len(le_gaps), 1))
    learning_effort = max(0, min(1, learning_effort))

    # ── 3. Distraction score (lower is better → invert) ────
    dist_gaps = []
    dist_gaps.append(_gap_less("Screen time/day", daily.screen_time,
                               bench["max_screen_time"], "Time Waste Regret"))
    dist_gaps.append(_gap_less("Distraction hours/day", daily.distraction_hours,
                               bench["max_distraction"], "Time Waste Regret"))
    distraction = 1 - (sum(dist_gaps) / max(len(dist_gaps), 1))
    distraction = max(0, min(1, distraction))

    # ── 4. Consistency & Productivity score ─────────────────
    consistency  = weekly.consistency_level / 10.0
    productivity = weekly.focus_level / 10.0

    # ── 5. Health check ─────────────────────────────────────
    _gap_less("Sleep deficit", max(0, bench["min_sleep"] - daily.sleep_hours),
              1, "Health Regret")
    _gap_more("Exercise hours/day", daily.exercise_hours,
              bench["exercise_hours"], "Health Regret")

    # ── Pack sub‑scores ─────────────────────────────────────
    result.sub_scores = {
        "consistency":     round(consistency, 3),
        "productivity":    round(productivity, 3),
        "distraction":     round(distraction, 3),
        "goal_alignment":  round(goal_alignment, 3),
        "learning_effort": round(learning_effort, 3),
    }

    return result
