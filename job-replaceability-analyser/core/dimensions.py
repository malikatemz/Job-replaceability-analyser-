"""
core/dimensions.py

Scoring dimension definitions and per-dimension scoring logic.
Each dimension returns a 0-100 score and a reasoning string.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .taxonomy import Role


@dataclass
class Dimension:
    id: str
    name: str
    description: str
    scorer: Callable[["Role"], "DimensionScore"]


@dataclass
class DimensionScore:
    dimension_id: str
    value: int          # 0–100; higher = more replaceable on this dimension
    reasoning: str


# ---------------------------------------------------------------------------
# Individual dimension scorers
# ---------------------------------------------------------------------------

def _score_task_routineness(role: "Role") -> DimensionScore:
    """
    How repetitive and rule-bound are the role's core tasks?
    High routineness → higher replaceability on this dimension.
    """
    score = role.task_routineness_score
    if score >= 70:
        reasoning = (
            f"{role.canonical_name} primarily involves structured, repeatable tasks "
            "such as log triage, alert classification, or compliance checklist review — "
            "all well within current automation reach."
        )
    elif score >= 40:
        reasoning = (
            f"{role.canonical_name} mixes routine procedural work with irregular, "
            "context-dependent tasks that resist full automation."
        )
    else:
        reasoning = (
            f"{role.canonical_name} involves highly variable, non-routine work — "
            "novel threat research, adversarial creativity, or strategic judgment — "
            "where automation has limited foothold."
        )
    return DimensionScore("task_routineness", score, reasoning)


def _score_data_dependency(role: "Role") -> DimensionScore:
    """
    Does the role operate primarily on structured, machine-readable data?
    High data dependency → higher replaceability.
    """
    score = role.data_dependency_score
    if score >= 70:
        reasoning = (
            "The role works predominantly with structured logs, SIEM alerts, "
            "CVE databases, or network telemetry — data AI consumes natively."
        )
    elif score >= 40:
        reasoning = (
            "The role uses a mix of structured data and unstructured sources "
            "(client conversations, threat reports, adversarial contexts)."
        )
    else:
        reasoning = (
            "The role relies heavily on qualitative, contextual, or human-derived "
            "information that is difficult to encode as machine-readable input."
        )
    return DimensionScore("data_dependency", score, reasoning)


def _score_judgment_intensity(role: "Role") -> DimensionScore:
    """
    How much does the role depend on contextual reasoning and ethical judgment?
    High judgment intensity → lower replaceability (inverted for composite).
    """
    raw = role.judgment_intensity_score
    # Invert: high judgment = lower replaceability score
    score = 100 - raw
    if score <= 30:
        reasoning = (
            f"{role.canonical_name} requires sustained high-stakes judgment — "
            "incident attribution, legal/regulatory reasoning, adversarial inference — "
            "that current AI cannot reliably replicate."
        )
    elif score <= 60:
        reasoning = (
            "The role involves meaningful judgment but also significant procedural "
            "components where AI can provide strong decision support."
        )
    else:
        reasoning = (
            "Core decisions in this role follow well-defined rules and playbooks, "
            "making them amenable to AI-driven automation or augmentation."
        )
    return DimensionScore("judgment_intensity", score, reasoning)


def _score_social_adversarial_complexity(role: "Role") -> DimensionScore:
    """
    How much does the role require human interaction, negotiation, or adversarial creativity?
    High complexity → lower replaceability (inverted).
    """
    raw = role.social_adversarial_score
    score = 100 - raw
    if score <= 30:
        reasoning = (
            "This role demands deep adversarial creativity, stakeholder negotiation, "
            "or red-team ingenuity — distinctly human capabilities in 2025."
        )
    elif score <= 60:
        reasoning = (
            "Some client-facing or creative adversarial elements exist alongside "
            "more automatable analytical components."
        )
    else:
        reasoning = (
            "The role is primarily analytical with limited social or adversarial "
            "creative demands, reducing this dimension's protective effect."
        )
    return DimensionScore("social_adversarial_complexity", score, reasoning)


def _score_tool_augmentation_ceiling(role: "Role") -> DimensionScore:
    """
    How much AI tooling is already deployed — and how much headroom remains?
    High ceiling reached → higher replaceability.
    """
    score = role.tool_augmentation_ceiling_score
    if score >= 70:
        reasoning = (
            "Mature AI tooling (SIEM automation, vulnerability scanners, SOAR playbooks) "
            "already covers most of this role's core tasks, with further automation "
            "commercially available or in active development."
        )
    elif score >= 40:
        reasoning = (
            "AI augmentation is active but partial — tools cover commodity tasks "
            "while higher-complexity work remains human-led."
        )
    else:
        reasoning = (
            "AI tooling for this role's core tasks is nascent or limited, "
            "reducing near-term automation exposure."
        )
    return DimensionScore("tool_augmentation_ceiling", score, reasoning)


# ---------------------------------------------------------------------------
# Dimension registry
# ---------------------------------------------------------------------------

DIMENSIONS: dict[str, Dimension] = {
    "task_routineness": Dimension(
        id="task_routineness",
        name="Task routineness",
        description="How repetitive and rule-bound the role's core tasks are",
        scorer=_score_task_routineness,
    ),
    "data_dependency": Dimension(
        id="data_dependency",
        name="Data dependency",
        description="Whether the role operates primarily on structured, machine-readable data",
        scorer=_score_data_dependency,
    ),
    "judgment_intensity": Dimension(
        id="judgment_intensity",
        name="Judgment intensity",
        description="Degree to which decisions require contextual reasoning and ethical weight",
        scorer=_score_judgment_intensity,
    ),
    "social_adversarial_complexity": Dimension(
        id="social_adversarial_complexity",
        name="Social & adversarial complexity",
        description="Human interaction, negotiation, red-teaming creativity, and novel threat response",
        scorer=_score_social_adversarial_complexity,
    ),
    "tool_augmentation_ceiling": Dimension(
        id="tool_augmentation_ceiling",
        name="Tool augmentation ceiling",
        description="How much AI tooling is already deployed and how much headroom remains",
        scorer=_score_tool_augmentation_ceiling,
    ),
}


def compute_dimension_score(dimension: Dimension, role: "Role") -> DimensionScore:
    return dimension.scorer(role)
