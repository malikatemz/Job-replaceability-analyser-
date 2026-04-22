"""
api/routes.py

FastAPI application — REST endpoints for the Job Replaceability Analyser.
Run with: uvicorn api.routes:app --reload
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from .schemas import (
    AnalyseRequest,
    AnalyseResponse,
    TeamAnalyseRequest,
    TeamAnalyseResponse,
    RoleListResponse,
    HealthResponse,
)
from .auth import verify_api_key
from core import analyse_role, analyse_team, list_available_roles
from core.projections import projection_narrative

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Job Replaceability Analyser API",
    description=(
        "Assess how vulnerable cybersecurity roles are to replacement "
        "by AI and automation."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse, tags=["system"])
def health_check():
    """Service liveness check."""
    return {"status": "ok", "version": "1.0.0"}


# ---------------------------------------------------------------------------
# Single role analysis
# ---------------------------------------------------------------------------

@app.post(
    "/analyse",
    response_model=AnalyseResponse,
    tags=["analysis"],
    summary="Analyse a single cybersecurity role",
)
def analyse(
    request: AnalyseRequest,
    _: None = Depends(verify_api_key),
):
    """
    Compute a replaceability index for a single cybersecurity role.

    Returns a 0–100 score, per-dimension breakdown, 5-year projection,
    task risk classification, and recommended upskilling paths.
    """
    try:
        result = analyse_role(
            role_name=request.role,
            specialisation=request.specialisation,
            experience_years=request.experience_years,
            sector=request.sector,
        )
    except Exception as exc:
        logger.exception("Error analysing role '%s'", request.role)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    narrative = projection_narrative(result.replaceability_index, result.projection)

    return AnalyseResponse(
        **result.to_dict(),
        projection_narrative=narrative,
    )


# ---------------------------------------------------------------------------
# Team analysis
# ---------------------------------------------------------------------------

@app.post(
    "/analyse/team",
    response_model=TeamAnalyseResponse,
    tags=["analysis"],
    summary="Analyse a team of roles and return aggregated risk profile",
)
def analyse_team_endpoint(
    request: TeamAnalyseRequest,
    _: None = Depends(verify_api_key),
):
    """
    Analyse multiple roles and return an aggregated team risk profile
    including tier distribution and individual role breakdowns.
    """
    if not request.roles:
        raise HTTPException(status_code=400, detail="roles list must not be empty")
    if len(request.roles) > 200:
        raise HTTPException(status_code=400, detail="Maximum 200 roles per team request")

    try:
        result = analyse_team(
            roles=[r.model_dump() for r in request.roles],
            sector=request.sector,
        )
    except Exception as exc:
        logger.exception("Error analysing team")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return TeamAnalyseResponse(**result)


# ---------------------------------------------------------------------------
# Role catalogue
# ---------------------------------------------------------------------------

@app.get(
    "/roles",
    response_model=RoleListResponse,
    tags=["roles"],
    summary="List all supported role profiles",
)
def get_roles(_: None = Depends(verify_api_key)):
    """Return the full catalogue of supported cybersecurity role profiles."""
    roles = list_available_roles()
    return RoleListResponse(count=len(roles), roles=roles)


@app.get(
    "/roles/{slug}",
    tags=["roles"],
    summary="Get a single role profile by slug",
)
def get_role(slug: str, _: None = Depends(verify_api_key)):
    """
    Retrieve the full profile and task breakdown for a specific role slug.
    Use GET /roles to discover available slugs.
    """
    import json
    from pathlib import Path
    path = Path(__file__).parent.parent / "data" / "roles" / f"{slug}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"No role profile found for slug '{slug}'")
    with open(path) as f:
        return json.load(f)
