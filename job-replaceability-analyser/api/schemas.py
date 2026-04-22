"""
api/schemas.py

Pydantic models for API request and response validation.
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------

class AnalyseRequest(BaseModel):
    role: str = Field(..., min_length=2, max_length=120, examples=["SOC Analyst Tier 1"])
    specialisation: Optional[str] = Field(None, examples=["cloud", "web", "network"])
    experience_years: int = Field(5, ge=0, le=50)
    sector: str = Field("general", examples=["financial_services", "government", "technology"])

    @field_validator("role")
    @classmethod
    def role_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("role must not be blank")
        return v.strip()


class TeamRoleEntry(BaseModel):
    role: str = Field(..., min_length=2, max_length=120)
    specialisation: Optional[str] = None
    experience_years: int = Field(5, ge=0, le=50)
    sector: Optional[str] = None


class TeamAnalyseRequest(BaseModel):
    roles: list[TeamRoleEntry] = Field(..., min_length=1)
    sector: str = Field("general", description="Default sector applied to roles without an explicit sector")


# ---------------------------------------------------------------------------
# Responses
# ---------------------------------------------------------------------------

class DimensionBreakdown(BaseModel):
    task_routineness: int
    data_dependency: int
    judgment_intensity: int
    social_adversarial_complexity: int
    tool_augmentation_ceiling: int


class ProjectionBreakdown(BaseModel):
    year_1: int
    year_3: int
    year_5: int


class AnalyseResponse(BaseModel):
    role: str
    specialisation: Optional[str]
    experience_years: int
    sector: str
    replaceability_index: int = Field(..., ge=0, le=100)
    risk_tier: str
    risk_description: str
    dimensions: dict[str, int]
    projection: dict[str, int]
    projection_narrative: str
    high_risk_tasks: list[str]
    low_risk_tasks: list[str]
    recommended_skills: list[str]
    reasoning: dict[str, str]


class TeamRoleResult(BaseModel):
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
    reasoning: dict[str, str]


class TeamAnalyseResponse(BaseModel):
    team_size: int
    average_replaceability_index: int
    average_risk_tier: str
    average_risk_description: str
    tier_distribution: dict[str, int]
    roles: list[dict]


class RoleEntry(BaseModel):
    slug: str
    canonical_name: str
    family: str
    description: str


class RoleListResponse(BaseModel):
    count: int
    roles: list[RoleEntry]


class HealthResponse(BaseModel):
    status: str
    version: str
