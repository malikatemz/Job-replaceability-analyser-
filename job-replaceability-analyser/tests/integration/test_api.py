"""
tests/integration/test_api.py

Integration tests for the FastAPI endpoints.
Uses httpx TestClient — no live server required.
"""

import os
import pytest
from fastapi.testclient import TestClient

# Put in dev mode so API key auth is bypassed
os.environ["ANALYSER_ENV"] = "development"

from api.routes import app  # noqa: E402 — env must be set first

client = TestClient(app)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

class TestHealth:
    def test_health_ok(self):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


# ---------------------------------------------------------------------------
# POST /analyse
# ---------------------------------------------------------------------------

class TestAnalyse:
    def test_basic_request(self):
        r = client.post("/analyse", json={"role": "SOC Analyst Tier 1"})
        assert r.status_code == 200
        data = r.json()
        assert "replaceability_index" in data
        assert 0 <= data["replaceability_index"] <= 100

    def test_risk_tier_present(self):
        r = client.post("/analyse", json={"role": "CISO"})
        assert r.status_code == 200
        assert "risk_tier" in r.json()

    def test_dimensions_present(self):
        r = client.post("/analyse", json={"role": "Penetration Tester"})
        data = r.json()
        assert "dimensions" in data
        assert "task_routineness" in data["dimensions"]

    def test_projection_present(self):
        r = client.post("/analyse", json={"role": "GRC Analyst"})
        data = r.json()
        assert "projection" in data
        assert "year_5" in data["projection"]

    def test_projection_narrative_present(self):
        r = client.post("/analyse", json={"role": "Incident Responder"})
        data = r.json()
        assert "projection_narrative" in data
        assert len(data["projection_narrative"]) > 10

    def test_with_specialisation(self):
        r = client.post("/analyse", json={
            "role": "Penetration Tester",
            "specialisation": "cloud",
        })
        assert r.status_code == 200

    def test_with_sector_and_experience(self):
        r = client.post("/analyse", json={
            "role": "SOC Analyst Tier 1",
            "sector": "financial_services",
            "experience_years": 10,
        })
        assert r.status_code == 200

    def test_empty_role_rejected(self):
        r = client.post("/analyse", json={"role": "   "})
        assert r.status_code == 422

    def test_missing_role_rejected(self):
        r = client.post("/analyse", json={})
        assert r.status_code == 422

    def test_high_risk_tasks_present(self):
        r = client.post("/analyse", json={"role": "SOC Analyst Tier 1"})
        data = r.json()
        assert isinstance(data["high_risk_tasks"], list)
        assert len(data["high_risk_tasks"]) > 0

    def test_recommended_skills_present(self):
        r = client.post("/analyse", json={"role": "SOC Analyst Tier 1"})
        data = r.json()
        assert isinstance(data["recommended_skills"], list)


# ---------------------------------------------------------------------------
# POST /analyse/team
# ---------------------------------------------------------------------------

class TestAnalyseTeam:
    def test_basic_team(self):
        r = client.post("/analyse/team", json={
            "roles": [
                {"role": "SOC Analyst Tier 1"},
                {"role": "CISO"},
                {"role": "GRC Analyst"},
            ],
            "sector": "general",
        })
        assert r.status_code == 200
        data = r.json()
        assert data["team_size"] == 3

    def test_average_index_in_range(self):
        r = client.post("/analyse/team", json={
            "roles": [{"role": "Penetration Tester"}, {"role": "SOC Analyst Tier 1"}],
            "sector": "technology",
        })
        data = r.json()
        assert 0 <= data["average_replaceability_index"] <= 100

    def test_tier_distribution_sums_correctly(self):
        roles = [{"role": r} for r in [
            "SOC Analyst Tier 1", "CISO", "GRC Analyst", "Penetration Tester"
        ]]
        r = client.post("/analyse/team", json={"roles": roles, "sector": "general"})
        data = r.json()
        assert sum(data["tier_distribution"].values()) == data["team_size"]

    def test_empty_roles_rejected(self):
        # Pydantic enforces min_length=1 on the roles list; FastAPI returns 422
        r = client.post("/analyse/team", json={"roles": [], "sector": "general"})
        assert r.status_code in (400, 422)

    def test_roles_included_in_response(self):
        r = client.post("/analyse/team", json={
            "roles": [{"role": "CISO"}],
            "sector": "general",
        })
        data = r.json()
        assert len(data["roles"]) == 1


# ---------------------------------------------------------------------------
# GET /roles
# ---------------------------------------------------------------------------

class TestRoles:
    def test_list_roles(self):
        r = client.get("/roles")
        assert r.status_code == 200
        data = r.json()
        assert "roles" in data
        assert isinstance(data["roles"], list)
        assert data["count"] == len(data["roles"])

    def test_roles_have_required_fields(self):
        r = client.get("/roles")
        for role in r.json()["roles"]:
            assert "slug" in role
            assert "canonical_name" in role
            assert "family" in role

    def test_get_single_role(self):
        r = client.get("/roles/soc_analyst_t1")
        assert r.status_code == 200
        data = r.json()
        assert "canonical_name" in data

    def test_get_unknown_role_404(self):
        r = client.get("/roles/nonexistent_role_xyz")
        assert r.status_code == 404
