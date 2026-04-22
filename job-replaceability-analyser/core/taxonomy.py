"""
core/taxonomy.py

Cybersecurity role taxonomy, Role dataclass, and profile loader.
Role profiles are stored as JSON under data/roles/.
A fuzzy name-matching fallback handles common synonyms and abbreviations.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data" / "roles"

# Canonical name → file slug mapping for common synonyms / abbreviations
ROLE_ALIASES: dict[str, str] = {
    # SOC
    "soc analyst": "soc_analyst_t1",
    "soc analyst tier 1": "soc_analyst_t1",
    "soc analyst tier 2": "soc_analyst_t2",
    "soc analyst tier 3": "soc_analyst_t3",
    "security operations analyst": "soc_analyst_t2",
    # Threat Intel
    "threat intelligence analyst": "threat_intel_analyst",
    "cti analyst": "threat_intel_analyst",
    "cyber threat intelligence": "threat_intel_analyst",
    # Incident Response
    "incident responder": "incident_responder",
    "incident response analyst": "incident_responder",
    "dfir analyst": "incident_responder",
    # Pen testing
    "penetration tester": "penetration_tester",
    "pen tester": "penetration_tester",
    "pentester": "penetration_tester",
    # Red Team
    "red team operator": "red_team_operator",
    "red teamer": "red_team_operator",
    # GRC
    "grc analyst": "grc_analyst",
    "compliance analyst": "grc_analyst",
    "risk analyst": "grc_analyst",
    # Engineering
    "security engineer": "security_engineer",
    "appsec engineer": "security_engineer",
    "devsecops engineer": "devsecops_engineer",
    "devsecops": "devsecops_engineer",
    # Architecture
    "cloud security architect": "cloud_security_architect",
    "security architect": "cloud_security_architect",
    # CISO
    "ciso": "ciso",
    "chief information security officer": "ciso",
    # AI/ML
    "ai security researcher": "ai_security_researcher",
    "adversarial ml": "adversarial_ml_specialist",
    "adversarial ml specialist": "adversarial_ml_specialist",
    # IAM
    "iam specialist": "iam_specialist",
    "identity and access management": "iam_specialist",
}


@dataclass
class Role:
    canonical_name: str
    family: str                          # e.g. "blue_team", "red_team", "grc"
    description: str

    # Raw dimension inputs (0–100)
    task_routineness_score: int
    data_dependency_score: int
    judgment_intensity_score: int        # High = lots of judgment (inverted in scorer)
    social_adversarial_score: int        # High = complex human/adversarial element (inverted)
    tool_augmentation_ceiling_score: int

    high_risk_tasks: list[str] = field(default_factory=list)
    low_risk_tasks: list[str] = field(default_factory=list)
    recommended_skills: list[str] = field(default_factory=list)
    specialisations: list[str] = field(default_factory=list)


def _normalise(name: str) -> str:
    return name.lower().strip()


def _slug_from_name(name: str) -> Optional[str]:
    """Resolve a role name to a data file slug via alias map or direct match."""
    normalised = _normalise(name)
    if normalised in ROLE_ALIASES:
        return ROLE_ALIASES[normalised]
    # Try direct file match (replace spaces with underscores)
    candidate = normalised.replace(" ", "_").replace("-", "_")
    if (DATA_DIR / f"{candidate}.json").exists():
        return candidate
    return None


def load_role_profile(role_name: str, specialisation: Optional[str] = None) -> Role:
    """
    Load a Role from the data/roles/ directory.
    Falls back to a synthetic profile if no file is found,
    logging a warning so operators know to add a proper profile.
    """
    slug = _slug_from_name(role_name)

    if slug and (DATA_DIR / f"{slug}.json").exists():
        with open(DATA_DIR / f"{slug}.json") as f:
            data = json.load(f)

        # Apply specialisation overrides if present
        if specialisation and specialisation in data.get("specialisation_overrides", {}):
            overrides = data["specialisation_overrides"][specialisation]
            data.update(overrides)

        return Role(
            canonical_name=data.get("canonical_name", role_name.title()),
            family=data.get("family", "unknown"),
            description=data.get("description", ""),
            task_routineness_score=data["task_routineness_score"],
            data_dependency_score=data["data_dependency_score"],
            judgment_intensity_score=data["judgment_intensity_score"],
            social_adversarial_score=data["social_adversarial_score"],
            tool_augmentation_ceiling_score=data["tool_augmentation_ceiling_score"],
            high_risk_tasks=data.get("high_risk_tasks", []),
            low_risk_tasks=data.get("low_risk_tasks", []),
            recommended_skills=data.get("recommended_skills", []),
            specialisations=data.get("specialisations", []),
        )

    # Synthetic fallback — mid-range scores with a warning
    logger.warning(
        "No profile found for role '%s' (slug: %s). "
        "Using synthetic mid-range scores. Add a profile to data/roles/ for accuracy.",
        role_name, slug,
    )
    return _synthetic_profile(role_name)


def _synthetic_profile(role_name: str) -> Role:
    return Role(
        canonical_name=role_name.title(),
        family="unknown",
        description="Synthetic profile — no matching role definition found.",
        task_routineness_score=50,
        data_dependency_score=50,
        judgment_intensity_score=50,
        social_adversarial_score=50,
        tool_augmentation_ceiling_score=50,
        high_risk_tasks=["Routine data processing", "Report generation"],
        low_risk_tasks=["Contextual judgment", "Novel problem solving"],
        recommended_skills=[
            "Adversarial AI literacy",
            "Human-AI teaming",
            "Domain-specific expertise deepening",
        ],
    )


def list_available_roles() -> list[dict]:
    """Return a list of all role profiles available in data/roles/."""
    roles = []
    for path in sorted(DATA_DIR.glob("*.json")):
        try:
            with open(path) as f:
                data = json.load(f)
            roles.append({
                "slug": path.stem,
                "canonical_name": data.get("canonical_name", path.stem),
                "family": data.get("family", "unknown"),
                "description": data.get("description", ""),
            })
        except Exception as e:
            logger.warning("Could not read role profile %s: %s", path, e)
    return roles
