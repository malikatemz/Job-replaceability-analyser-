"""
tests/unit/test_scorer.py

Unit tests for the core scoring engine and projection model.
"""

import pytest
from unittest.mock import patch, MagicMock

from core.scorer import (
    analyse_role,
    analyse_team,
    classify_risk,
    apply_experience_modifier,
    apply_sector_modifier,
    ReplaceabilityResult,
)
from core.projections import project_replaceability, projection_narrative
from core.taxonomy import _normalise, _slug_from_name, load_role_profile


# ---------------------------------------------------------------------------
# classify_risk
# ---------------------------------------------------------------------------

class TestClassifyRisk:
    def test_very_low(self):
        tier, _ = classify_risk(10)
        assert tier == "very_low"

    def test_low(self):
        tier, _ = classify_risk(35)
        assert tier == "low"

    def test_moderate(self):
        tier, _ = classify_risk(55)
        assert tier == "moderate"

    def test_high(self):
        tier, _ = classify_risk(68)
        assert tier == "high"

    def test_very_high(self):
        tier, _ = classify_risk(85)
        assert tier == "very_high"

    def test_boundary_25(self):
        tier, _ = classify_risk(25)
        assert tier == "very_low"

    def test_boundary_26(self):
        tier, _ = classify_risk(26)
        assert tier == "low"

    def test_boundary_100(self):
        tier, _ = classify_risk(100)
        assert tier == "very_high"

    def test_returns_description(self):
        _, desc = classify_risk(50)
        assert isinstance(desc, str)
        assert len(desc) > 0


# ---------------------------------------------------------------------------
# apply_experience_modifier
# ---------------------------------------------------------------------------

class TestExperienceModifier:
    def test_senior_gets_reduction(self):
        base = 60
        adjusted = apply_experience_modifier(base, experience_years=15)
        assert adjusted < base

    def test_junior_gets_increase(self):
        base = 40
        adjusted = apply_experience_modifier(base, experience_years=1)
        assert adjusted > base

    def test_mid_level_unchanged(self):
        base = 50
        adjusted = apply_experience_modifier(base, experience_years=5)
        assert adjusted == base

    def test_clamped_at_zero(self):
        adjusted = apply_experience_modifier(5, experience_years=20)
        assert adjusted >= 0

    def test_clamped_at_100(self):
        adjusted = apply_experience_modifier(99, experience_years=1)
        assert adjusted <= 100


# ---------------------------------------------------------------------------
# apply_sector_modifier
# ---------------------------------------------------------------------------

class TestSectorModifier:
    MODIFIERS = {
        "technology": 1.10,
        "government": 0.90,
        "general": 1.00,
    }

    def test_technology_increases(self):
        result = apply_sector_modifier(50, "technology", self.MODIFIERS)
        assert result == 55

    def test_government_decreases(self):
        result = apply_sector_modifier(50, "government", self.MODIFIERS)
        assert result == 45

    def test_general_unchanged(self):
        result = apply_sector_modifier(50, "general", self.MODIFIERS)
        assert result == 50

    def test_unknown_sector_defaults_to_1(self):
        result = apply_sector_modifier(50, "unknown_sector", self.MODIFIERS)
        assert result == 50

    def test_result_clamped(self):
        result = apply_sector_modifier(98, "technology", self.MODIFIERS)
        assert result <= 100


# ---------------------------------------------------------------------------
# project_replaceability
# ---------------------------------------------------------------------------

class TestProjectReplaceability:
    def test_returns_three_years(self):
        proj = project_replaceability(40)
        assert set(proj.keys()) == {"year_1", "year_3", "year_5"}

    def test_projection_never_decreases(self):
        proj = project_replaceability(40)
        assert proj["year_1"] >= 40
        assert proj["year_3"] >= proj["year_1"]
        assert proj["year_5"] >= proj["year_3"]

    def test_cap_at_95(self):
        proj = project_replaceability(90)
        for v in proj.values():
            assert v <= 95

    def test_low_index_grows_slowly(self):
        proj = project_replaceability(10, ai_growth_rate=0.18)
        # Very low replaceability roles should not jump dramatically in year 1
        assert proj["year_1"] - 10 < 10

    def test_high_index_approaches_cap(self):
        proj = project_replaceability(75, ai_growth_rate=0.30, adoption_lag=0.5)
        assert proj["year_5"] >= 80

    def test_all_values_integer(self):
        proj = project_replaceability(50)
        for v in proj.values():
            assert isinstance(v, int)


class TestProjectionNarrative:
    def test_returns_string(self):
        proj = project_replaceability(40)
        narrative = projection_narrative(40, proj)
        assert isinstance(narrative, str)
        assert len(narrative) > 20

    def test_mentions_current_index(self):
        proj = {"year_1": 42, "year_3": 48, "year_5": 55}
        narrative = projection_narrative(40, proj)
        assert "40" in narrative

    def test_tier_change_mentioned(self):
        # 25 → 55 crosses from very_low/low into moderate
        proj = {"year_1": 35, "year_3": 45, "year_5": 55}
        narrative = projection_narrative(25, proj)
        assert "tier" in narrative.lower()


# ---------------------------------------------------------------------------
# taxonomy
# ---------------------------------------------------------------------------

class TestTaxonomy:
    def test_normalise_lowercase(self):
        assert _normalise("SOC Analyst") == "soc analyst"

    def test_normalise_strips(self):
        assert _normalise("  pen tester  ") == "pen tester"

    def test_slug_from_known_alias(self):
        assert _slug_from_name("pen tester") == "penetration_tester"

    def test_slug_from_canonical(self):
        assert _slug_from_name("SOC Analyst Tier 1") == "soc_analyst_t1"

    def test_slug_unknown_returns_none_or_str(self):
        result = _slug_from_name("quantum cryptographer")
        # May be None or a non-existent slug — either is acceptable
        assert result is None or isinstance(result, str)

    def test_load_soc_t1(self):
        role = load_role_profile("SOC Analyst Tier 1")
        assert role.canonical_name == "SOC Analyst Tier 1"
        assert 0 <= role.task_routineness_score <= 100
        assert len(role.high_risk_tasks) > 0

    def test_load_unknown_returns_synthetic(self):
        role = load_role_profile("Quantum Security Wizard")
        assert role.task_routineness_score == 50  # synthetic fallback
        assert "synthetic" in role.description.lower()


# ---------------------------------------------------------------------------
# analyse_role (integration-ish, uses real profiles)
# ---------------------------------------------------------------------------

class TestAnalyseRole:
    def test_returns_result_object(self):
        result = analyse_role("SOC Analyst Tier 1")
        assert isinstance(result, ReplaceabilityResult)

    def test_index_in_range(self):
        result = analyse_role("SOC Analyst Tier 1")
        assert 0 <= result.replaceability_index <= 100

    def test_risk_tier_set(self):
        result = analyse_role("SOC Analyst Tier 1")
        assert result.risk_tier in ("very_low", "low", "moderate", "high", "very_high")

    def test_soc_t1_higher_than_ciso(self):
        soc = analyse_role("SOC Analyst Tier 1")
        ciso = analyse_role("CISO")
        assert soc.replaceability_index > ciso.replaceability_index

    def test_pen_tester_lower_than_soc_t1(self):
        pen = analyse_role("Penetration Tester")
        soc = analyse_role("SOC Analyst Tier 1")
        assert pen.replaceability_index < soc.replaceability_index

    def test_dimensions_keys_present(self):
        result = analyse_role("Penetration Tester")
        expected_keys = {
            "task_routineness", "data_dependency",
            "judgment_intensity", "social_adversarial_complexity",
            "tool_augmentation_ceiling",
        }
        assert expected_keys.issubset(result.dimensions.keys())

    def test_projection_present(self):
        result = analyse_role("GRC Analyst")
        assert "year_5" in result.projection

    def test_to_dict_serialisable(self):
        import json
        result = analyse_role("Incident Responder")
        d = result.to_dict()
        # Must be JSON-serialisable
        json.dumps(d)

    def test_sector_affects_score(self):
        tech = analyse_role("GRC Analyst", sector="technology")
        gov = analyse_role("GRC Analyst", sector="government")
        assert tech.replaceability_index > gov.replaceability_index

    def test_experience_affects_score(self):
        junior = analyse_role("SOC Analyst Tier 1", experience_years=1)
        senior = analyse_role("SOC Analyst Tier 1", experience_years=20)
        assert junior.replaceability_index > senior.replaceability_index


# ---------------------------------------------------------------------------
# analyse_team
# ---------------------------------------------------------------------------

class TestAnalyseTeam:
    def test_returns_dict(self):
        result = analyse_team([
            {"role": "SOC Analyst Tier 1"},
            {"role": "CISO"},
        ])
        assert isinstance(result, dict)

    def test_team_size_correct(self):
        result = analyse_team([
            {"role": "SOC Analyst Tier 1"},
            {"role": "Penetration Tester"},
            {"role": "GRC Analyst"},
        ])
        assert result["team_size"] == 3

    def test_average_index_in_range(self):
        result = analyse_team([
            {"role": "SOC Analyst Tier 1"},
            {"role": "Incident Responder"},
        ])
        assert 0 <= result["average_replaceability_index"] <= 100

    def test_tier_distribution_sums_to_team_size(self):
        roles = [{"role": r} for r in ["SOC Analyst Tier 1", "CISO", "GRC Analyst"]]
        result = analyse_team(roles)
        assert sum(result["tier_distribution"].values()) == result["team_size"]

    def test_roles_list_in_result(self):
        result = analyse_team([{"role": "CISO"}])
        assert len(result["roles"]) == 1
