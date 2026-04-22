"""
tests/conftest.py

Shared pytest fixtures for the Job Replaceability Analyser test suite.
"""

import os
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session", autouse=True)
def set_dev_mode():
    """Ensure API key auth is disabled for all tests."""
    os.environ["ANALYSER_ENV"] = "development"
    yield
    os.environ.pop("ANALYSER_ENV", None)


@pytest.fixture(scope="session")
def api_client():
    """Reusable FastAPI TestClient for integration tests."""
    from api.routes import app
    return TestClient(app)


@pytest.fixture
def sample_roles():
    return [
        {"role": "SOC Analyst Tier 1", "experience_years": 2, "sector": "general"},
        {"role": "Penetration Tester", "experience_years": 6, "sector": "technology"},
        {"role": "CISO", "experience_years": 15, "sector": "financial_services"},
        {"role": "GRC Analyst", "experience_years": 4, "sector": "government"},
        {"role": "Incident Responder", "experience_years": 5, "sector": "general"},
    ]


@pytest.fixture
def soc_t1_result():
    from core import analyse_role
    return analyse_role("SOC Analyst Tier 1", experience_years=3, sector="general")


@pytest.fixture
def ciso_result():
    from core import analyse_role
    return analyse_role("CISO", experience_years=15, sector="financial_services")
