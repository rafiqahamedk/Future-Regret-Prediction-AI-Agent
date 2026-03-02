"""
Module 4 — predictor.py
Generates human‑readable future scenario predictions for multiple
time horizons based on the regret analysis.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List
from regret_engine import RegretResult
from user_input import UserProfile
from config import TIME_HORIZONS


@dataclass
class ScenarioPrediction:
    horizon: str          # e.g. "6 months"
    summary: str          # single headline sentence
    details: List[str]    # bullet‑point predictions
    risk_level: str       # LOW / MODERATE / HIGH / CRITICAL


@dataclass
class PredictionReport:
    scenarios: List[ScenarioPrediction] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"scenarios": [asdict(s) for s in self.scenarios]}


# ── Prediction templates ────────────────────────────────────

_CAREER_TPL = {
    "LOW":      "Career trajectory looks healthy; keep the momentum.",
    "MODERATE": "Some career gaps are forming — they will compound if ignored.",
    "HIGH":     "Significant career risk detected. Placement and growth opportunities may slip away.",
    "CRITICAL": "Career derailment is likely without immediate intervention.",
}

_SKILL_TPL = {
    "LOW":      "Skill growth is on track for your goals.",
    "MODERATE": "Skill development is lagging slightly behind where it needs to be.",
    "HIGH":     "Major skill gaps are widening — you may not be job‑ready in time.",
    "CRITICAL": "Skill stagnation is severe; catching up will require intense effort.",
}

_TIME_TPL = {
    "LOW":      "Time is being used effectively.",
    "MODERATE": "Noticeable time is being lost to low‑value activities.",
    "HIGH":     "A large portion of your day is unproductive — future self will notice.",
    "CRITICAL": "Time waste is extreme. Years of potential growth are being lost.",
}

_HEALTH_TPL = {
    "LOW":      "Health habits are solid.",
    "MODERATE": "Minor health risks exist (sleep/exercise). Address early.",
    "HIGH":     "Declining health habits will affect energy and productivity.",
    "CRITICAL": "Health neglect is severe and will undermine every other goal.",
}

_FINANCIAL_TPL = {
    "LOW":      "Financial trajectory looks stable given career path.",
    "MODERATE": "Financial growth may slow due to skill and career gaps.",
    "HIGH":     "Earning potential is at risk — skill and career gaps limit opportunities.",
    "CRITICAL": "Serious financial consequences ahead if career and skill issues are not fixed.",
}

_TEMPLATES = {
    "Career Regret":     _CAREER_TPL,
    "Skill Regret":      _SKILL_TPL,
    "Time Waste Regret": _TIME_TPL,
    "Health Regret":     _HEALTH_TPL,
    "Financial Regret":  _FINANCIAL_TPL,
}


# ── Decay multipliers per horizon ──────────────────────────
# Longer horizons amplify the regret effect
_HORIZON_MULTIPLIER = {
    "3_months": 0.6,
    "6_months": 0.8,
    "1_year":   1.0,
    "2_years":  1.2,
}


def _risk_label(score: float) -> str:
    if score <= 30:
        return "LOW"
    if score <= 55:
        return "MODERATE"
    if score <= 75:
        return "HIGH"
    return "CRITICAL"


def predict(profile: UserProfile, regret: RegretResult) -> PredictionReport:
    """Generate scenario predictions for each time horizon."""

    report = PredictionReport()
    career = profile.basic.career_goal

    for key, label in TIME_HORIZONS.items():
        mult = _HORIZON_MULTIPLIER.get(key, 1.0)
        adjusted_score = min(100, regret.overall_score * mult)
        risk = _risk_label(adjusted_score)

        details: List[str] = []

        # Walk each regret category and pick the appropriate template line
        for cat in regret.categories:
            cat_adjusted = min(100, cat.score * mult)
            cat_risk = _risk_label(cat_adjusted)
            tpl = _TEMPLATES.get(cat.name, {})
            line = tpl.get(cat_risk, "")
            if line and cat_risk != "LOW":
                details.append(f"[{cat.name}] {line}")

        # Compose summary
        if risk == "LOW":
            summary = (f"If this routine continues for {label}, "
                       f"you are largely on track toward your {career} goal.")
        elif risk == "MODERATE":
            summary = (f"If this routine continues for {label}, "
                       f"noticeable gaps will develop in your {career} journey.")
        elif risk == "HIGH":
            summary = (f"If this routine continues for {label}, "
                       f"you risk missing important {career} milestones.")
        else:
            summary = (f"If this routine continues for {label}, "
                       f"serious setbacks in your {career} path are highly probable.")

        if not details:
            details.append("Overall habits are aligned with goals — maintain consistency.")

        report.scenarios.append(ScenarioPrediction(
            horizon=label,
            summary=summary,
            details=details,
            risk_level=risk,
        ))

    return report
