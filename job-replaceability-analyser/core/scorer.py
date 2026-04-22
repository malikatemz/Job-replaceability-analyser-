"""
core/scorer.py

Main scoring engine for the Job Replaceability Analyser.
Computes a 0-100 replaceability index for cybersecurity roles
across five weighted dimensions.
"""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .dimensions import DIMENSIONS, DimensionScore, compute_dimension_score
from .taxonomy import Role, load_role_profile
from .projections import project_replaceability

logger = logging.getLogger(__name__)

RISK_TIERS = [
    (0,  25,  "very_low",  "Highly resistant to automation in the near term"),
    (26, 45,  "low",       "Some routine tasks automatable; core requires human expertise"),
    (46, 60,  "moderate",  "Significant task displacement expected; upskilling advisable"),
    (61, 75,  "high",      "Most core tasks within reach of current or near-term AI tooling"),
    (76, 100, "very_high", "Role likely to be substantially restructured or absorbed"),
]


@dataclass
class ReplaceabilityResult:
    role: str
    specialisation: Optional[str]
    experience_years: int
    sector: str
    replaceability_index: int
    risk_tier: str
    risk_description: str
    dimensions: dict[str, int]
    projection: dict[str, int]
    high_risk_tasks: list[str]
    low_risk_tasks: list[str]
    recommended_skills: list[str]
    reasoning: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "specialisation": self.specialisation,
            "experience_years": self.experience_years,
            "sector": self.sector,
            "replaceability_index": self.replaceability_index,
            "risk_tier": self.risk_tier,
            "risk_description": self.risk_description,
            "dimensions": self.dimensions,
            "projection": self.projection,
            "high_risk_tasks": self.high_risk_tasks,
            "low_risk_tasks": self.low_risk_tasks,
            "recommended_skills": self.recommended_skills,
            "reasoning": self.reasoning,
        }


def classify_risk(index: int) -> tuple[str, str]:
    for lo, hi, tier, description in RISK_TIERS:
        if lo <= index <= hi:
            return tier, description
    return "unknown", "Unable to classify"


def apply_experience_modifier(raw_index: int, experience_years: int) -> int:
    """
    Senior practitioners are partially insulated from automation
    due to contextual judgment, institutional knowledge, and leadership.
    Apply a mild downward modifier for 8+ years of experience.
    """
    if experience_years >= 15:
        modifier = -8
    elif experience_years >= 8:
        modifier = -4
    elif experience_years <= 2:
        modifier = +3  # Early-career roles skew toward automatable tasks
    else:
        modifier = 0
    return max(0, min(100, raw_index + modifier))


def apply_sector_modifier(raw_index: int, sector: str, sector_modifiers: dict) -> int:
    multiplier = sector_modifiers.get(sector, 1.0)
    adjusted = round(raw_index * multiplier)
    return max(0, min(100, adjusted))


def analyse_role(
    role_name: str,
    specialisation: Optional[str] = None,
    experience_years: int = 5,
    sector: str = "general",
    settings: Optional[dict] = None,
) -> ReplaceabilityResult:
    """
    Core analysis function. Returns a full ReplaceabilityResult.

    Args:
        role_name:         Job title to analyse (e.g. "SOC Analyst Tier 1")
        specialisation:    Optional sub-specialisation (e.g. "cloud", "web")
        experience_years:  Years of experience in the role
        sector:            Industry sector (e.g. "financial_services", "government")
        settings:          Optional config overrides (dimension weights, sector modifiers)
    """
    if settings is None:
        settings = _default_settings()

    role: Role = load_role_profile(role_name, specialisation)
    dimension_weights: dict[str, float] = settings["scoring"]["dimension_weights"]
    sector_modifiers: dict[str, float] = settings["scoring"]["sector_modifiers"]

    # Score each dimension
    dimension_scores: dict[str, DimensionScore] = {}
    for dim_id, weight in dimension_weights.items():
        if dim_id not in DIMENSIONS:
            logger.warning("Unknown dimension '%s' in settings — skipping", dim_id)
            continue
        score = compute_dimension_score(DIMENSIONS[dim_id], role)
        dimension_scores[dim_id] = score

    # Weighted composite
    raw_index = round(
        sum(
            dimension_scores[d].value * dimension_weights[d]
            for d in dimension_scores
        )
    )

    # Apply modifiers
    index = apply_experience_modifier(raw_index, experience_years)
    index = apply_sector_modifier(index, sector, sector_modifiers)

    risk_tier, risk_description = classify_risk(index)

    projection = project_replaceability(
        current_index=index,
        ai_growth_rate=settings["projection"]["ai_capability_growth_rate"],
        adoption_lag=settings["projection"]["adoption_lag_years"],
    )

    reasoning = {d: ds.reasoning for d, ds in dimension_scores.items()}

    return ReplaceabilityResult(
        role=role.canonical_name,
        specialisation=specialisation,
        experience_years=experience_years,
        sector=sector,
        replaceability_index=index,
        risk_tier=risk_tier,
        risk_description=risk_description,
        dimensions={d: ds.value for d, ds in dimension_scores.items()},
        projection=projection,
        high_risk_tasks=role.high_risk_tasks,
        low_risk_tasks=role.low_risk_tasks,
        recommended_skills=role.recommended_skills,
        reasoning=reasoning,
    )


def analyse_team(
    roles: list[dict],
    sector: str = "general",
    settings: Optional[dict] = None,
) -> dict:
    """
    Analyse a list of roles and return aggregated team risk profile.

    Args:
        roles:   List of dicts with keys: role, specialisation (opt), experience_years (opt)
        sector:  Sector applied to all roles unless overridden per-role
        settings: Optional config overrides
    """
    results = []
    for entry in roles:
        r = analyse_role(
            role_name=entry["role"],
            specialisation=entry.get("specialisation"),
            experience_years=entry.get("experience_years", 5),
            sector=entry.get("sector", sector),
            settings=settings,
        )
        results.append(r.to_dict())

    indices = [r["replaceability_index"] for r in results]
    avg_index = round(sum(indices) / len(indices)) if indices else 0
    avg_tier, avg_desc = classify_risk(avg_index)

    tier_counts: dict[str, int] = {}
    for r in results:
        t = r["risk_tier"]
        tier_counts[t] = tier_counts.get(t, 0) + 1

    return {
        "team_size": len(results),
        "average_replaceability_index": avg_index,
        "average_risk_tier": avg_tier,
        "average_risk_description": avg_desc,
        "tier_distribution": tier_counts,
        "roles": results,
    }


def _default_settings() -> dict:
    config_path = Path(__file__).parent.parent / "config" / "settings.yaml"
    if config_path.exists():
        try:
            import yaml
            with open(config_path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning("Could not load settings.yaml (%s) — using defaults", e)

    return {
        "scoring": {
            "dimension_weights": {
                "task_routineness": 0.20,
                "data_dependency": 0.20,
                "judgment_intensity": 0.25,
                "social_adversarial_complexity": 0.20,
                "tool_augmentation_ceiling": 0.15,
            },
            "sector_modifiers": {
                "financial_services": 1.05,
                "government": 0.90,
                "healthcare": 0.95,
                "technology": 1.10,
                "general": 1.00,
            },
        },
        "projection": {
            "ai_capability_growth_rate": 0.18,
            "adoption_lag_years": 1.5,
        },
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _cli():
    parser = argparse.ArgumentParser(
        description="Analyse cybersecurity job replaceability by AI/automation"
    )
    parser.add_argument("--role", required=True, help="Job title to analyse")
    parser.add_argument("--specialisation", default=None)
    parser.add_argument("--experience", type=int, default=5, dest="experience_years")
    parser.add_argument("--sector", default="general")
    parser.add_argument("--output", default=None, help="Output file path (JSON)")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    result = analyse_role(
        role_name=args.role,
        specialisation=args.specialisation,
        experience_years=args.experience_years,
        sector=args.sector,
    )

    indent = 2 if args.pretty else None
    output_json = json.dumps(result.to_dict(), indent=indent)

    if args.output:
        Path(args.output).write_text(output_json)
        print(f"Result written to {args.output}")
    else:
        print(output_json)


if __name__ == "__main__":
    _cli()
