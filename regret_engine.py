"""
Module 3 — regret_engine.py
Calculates the Future Regret Score (0‑100) and classifies regret types.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List
from analyzer import AnalysisResult
from config import WEIGHTS, REGRET_THRESHOLDS, REGRET_TYPES


@dataclass
class RegretCategory:
    name: str
    score: float          # 0‑100
    severity: str         # LOW / MODERATE / HIGH / CRITICAL
    contributing_gaps: List[str] = field(default_factory=list)


@dataclass
class RegretResult:
    overall_score: float  # 0‑100
    overall_severity: str
    categories: List[RegretCategory] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "overall_score":    self.overall_score,
            "overall_severity": self.overall_severity,
            "categories":       [asdict(c) for c in self.categories],
        }


# ── Helpers ─────────────────────────────────────────────────

def _label(score: float) -> str:
    for label, (lo, hi) in REGRET_THRESHOLDS.items():
        if lo <= score <= hi:
            return label
    return "CRITICAL"


def _category_score(gaps, category_name: str) -> RegretCategory:
    """Average the severity of gaps belonging to a category → 0‑100 score."""
    sev_map = {"LOW": 15, "MODERATE": 40, "HIGH": 65, "CRITICAL": 90}
    relevant = [g for g in gaps if g.category == category_name]
    if not relevant:
        return RegretCategory(name=category_name, score=0, severity="LOW")
    avg = sum(sev_map.get(g.severity, 50) for g in relevant) / len(relevant)
    return RegretCategory(
        name=category_name,
        score=round(avg, 1),
        severity=_label(avg),
        contributing_gaps=[f"{g.metric} (gap {g.gap:+.1f})" for g in relevant
                           if g.severity in ("HIGH", "CRITICAL")],
    )


# ── Main engine ─────────────────────────────────────────────

def compute_regret(analysis: AnalysisResult) -> RegretResult:
    """
    Combine weighted sub‑scores into a single 0‑100 regret score.
    Higher score = higher risk of future regret.
    """

    ss = analysis.sub_scores
    # Each sub‑score is 0‑1 (1 = good). We invert so 1→0 regret, 0→100 regret.
    weighted_sum = 0.0
    for key, weight in WEIGHTS.items():
        value = ss.get(key, 0.5)
        weighted_sum += (1 - value) * weight  # invert
    overall = round(weighted_sum * 100, 1)
    overall = max(0, min(100, overall))

    # ── Per‑category scores ─────────────────────────────────
    categories = [_category_score(analysis.gaps, rt) for rt in REGRET_TYPES]

    return RegretResult(
        overall_score=overall,
        overall_severity=_label(overall),
        categories=categories,
    )
