"""
core — Job Replaceability Analyser engine.

Public API:
    analyse_role(role_name, ...)  → ReplaceabilityResult
    analyse_team(roles, ...)      → dict
"""

from .scorer import analyse_role, analyse_team, ReplaceabilityResult
from .taxonomy import list_available_roles

__all__ = [
    "analyse_role",
    "analyse_team",
    "ReplaceabilityResult",
    "list_available_roles",
]
