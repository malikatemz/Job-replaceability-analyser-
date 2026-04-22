"""
core/projections.py

Trend and timeline modelling for replaceability scores.
Projects how a role's replaceability index may change over 1, 3, and 5 years
based on an AI capability growth rate and an adoption lag factor.

Model rationale
---------------
We use a logistic growth curve capped at 95 (no role reaches 100% automation):

    projected(t) = cap / (1 + ((cap - index) / index) * exp(-k * (t - lag)))

where:
    cap   = 95
    index = current replaceability index
    k     = ai_capability_growth_rate (annual)
    lag   = adoption_lag_years (delay before growth takes full effect)
    t     = years into the future

For low-index roles (< 20) a floor of current_index is applied so the
projection never shows scores decreasing below the present value.
"""

from __future__ import annotations

import math


CAP = 95


def _logistic(index: float, k: float, t: float, lag: float) -> float:
    """
    Logistic growth projection anchored at `index` at t=0,
    with an adoption lag shifting the inflection point forward.
    """
    if index <= 0:
        return 0.0
    if index >= CAP:
        return float(CAP)

    effective_t = max(0.0, t - lag)
    ratio = (CAP - index) / index
    denominator = 1 + ratio * math.exp(-k * effective_t)
    return CAP / denominator


def project_replaceability(
    current_index: int,
    ai_growth_rate: float = 0.18,
    adoption_lag: float = 1.5,
) -> dict[str, int]:
    """
    Project replaceability index at 1, 3, and 5 years.

    Args:
        current_index:    Current 0–100 replaceability score
        ai_growth_rate:   Annual AI capability compound growth (default: 0.18 = 18%)
        adoption_lag:     Years before growth effect fully manifests (default: 1.5)

    Returns:
        Dict with keys "year_1", "year_3", "year_5"
    """
    projections = {}
    for years in (1, 3, 5):
        raw = _logistic(float(current_index), ai_growth_rate, float(years), adoption_lag)
        projected = max(current_index, round(raw))  # never decreases
        projections[f"year_{years}"] = min(projected, CAP)

    return projections


def projection_narrative(current_index: int, projection: dict[str, int]) -> str:
    """
    Generate a plain-English narrative for the projection.
    """
    delta_5 = projection["year_5"] - current_index
    tier_change = _tier_label(projection["year_5"]) != _tier_label(current_index)

    if delta_5 <= 5:
        pace = "relatively stable"
    elif delta_5 <= 15:
        pace = "a gradual upward trend"
    elif delta_5 <= 25:
        pace = "a significant increase"
    else:
        pace = "a steep increase"

    narrative = (
        f"Over the next five years the replaceability index is projected to move "
        f"from {current_index} to {projection['year_5']} — {pace}."
    )
    if tier_change:
        narrative += (
            f" This crosses a risk tier boundary, moving into "
            f"'{_tier_label(projection['year_5'])}' territory by year 5."
        )
    return narrative


def _tier_label(index: int) -> str:
    if index <= 25:
        return "very_low"
    if index <= 45:
        return "low"
    if index <= 60:
        return "moderate"
    if index <= 75:
        return "high"
    return "very_high"
