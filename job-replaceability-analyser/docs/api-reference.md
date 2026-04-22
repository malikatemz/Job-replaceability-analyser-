# API Reference

Base URL: `http://localhost:8000` (local) | `https://api.your-domain.com` (production)

Interactive docs available at `/docs` (Swagger UI) and `/redoc` (ReDoc) when the server is running.

---

## Authentication

All endpoints (except `/health`) require an `X-API-Key` header.

```
X-API-Key: your-secret-key-here
```

In development mode (`ANALYSER_ENV=development`), authentication is bypassed.

---

## Endpoints

### `GET /health`

Service liveness check. No authentication required.

**Response**
```json
{ "status": "ok", "version": "1.0.0" }
```

---

### `POST /analyse`

Analyse a single cybersecurity role.

**Request body**

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `role` | string | Yes | — | Job title to analyse |
| `specialisation` | string | No | null | Sub-specialisation (e.g. `"cloud"`, `"web"`) |
| `experience_years` | integer | No | 5 | Years of experience |
| `sector` | string | No | `"general"` | Industry sector |

**Example request**
```json
{
  "role": "SOC Analyst Tier 1",
  "specialisation": null,
  "experience_years": 3,
  "sector": "financial_services"
}
```

**Example response**
```json
{
  "role": "SOC Analyst Tier 1",
  "specialisation": null,
  "experience_years": 3,
  "sector": "financial_services",
  "replaceability_index": 76,
  "risk_tier": "very_high",
  "risk_description": "Role likely to be substantially restructured or absorbed",
  "dimensions": {
    "task_routineness": 78,
    "data_dependency": 82,
    "judgment_intensity": 72,
    "social_adversarial_complexity": 78,
    "tool_augmentation_ceiling": 80
  },
  "projection": {
    "year_1": 78,
    "year_3": 82,
    "year_5": 86
  },
  "projection_narrative": "Over the next five years the replaceability index is projected to move from 76 to 86 — a significant increase.",
  "high_risk_tasks": [
    "Alert triage and classification",
    "Log parsing and correlation",
    "Ticket creation and escalation"
  ],
  "low_risk_tasks": [
    "Novel attack pattern recognition",
    "Analyst intuition on edge cases"
  ],
  "recommended_skills": [
    "Threat hunting",
    "Malware analysis",
    "Cloud security fundamentals"
  ],
  "reasoning": {
    "task_routineness": "SOC Analyst Tier 1 primarily involves structured, repeatable tasks...",
    "data_dependency": "The role works predominantly with structured logs, SIEM alerts..."
  }
}
```

---

### `POST /analyse/team`

Analyse a team of roles and return an aggregated risk profile.

**Request body**

| Field | Type | Required | Description |
|---|---|---|---|
| `roles` | array | Yes | List of role entries (max 200) |
| `sector` | string | No | Default sector for roles without an explicit sector |

Each role entry accepts the same fields as a single `/analyse` request.

**Example request**
```json
{
  "roles": [
    { "role": "SOC Analyst Tier 1", "experience_years": 2 },
    { "role": "Incident Responder", "experience_years": 5 },
    { "role": "CISO", "experience_years": 15 }
  ],
  "sector": "technology"
}
```

**Example response**
```json
{
  "team_size": 3,
  "average_replaceability_index": 52,
  "average_risk_tier": "moderate",
  "average_risk_description": "Significant task displacement expected; upskilling advisable",
  "tier_distribution": {
    "very_high": 1,
    "moderate": 1,
    "very_low": 1
  },
  "roles": [ "...individual role results..." ]
}
```

---

### `GET /roles`

List all supported role profiles.

**Response**
```json
{
  "count": 12,
  "roles": [
    {
      "slug": "soc_analyst_t1",
      "canonical_name": "SOC Analyst Tier 1",
      "family": "blue_team",
      "description": "First-line security operations centre analyst..."
    }
  ]
}
```

---

### `GET /roles/{slug}`

Retrieve the full profile for a role by slug.

**Path parameter:** `slug` — use `GET /roles` to discover available slugs.

**Response:** Full role JSON profile including all dimension scores and task lists.

**Errors:**
- `404 Not Found` — no profile exists for the given slug

---

## Sector Values

| Value | Description |
|---|---|
| `general` | Default — no sector modifier applied |
| `financial_services` | Banking, insurance, capital markets |
| `government` | Central/local government, public sector |
| `healthcare` | Hospitals, pharma, medical devices |
| `technology` | Software, cloud, SaaS companies |
| `defence` | Military and defence contractors |
| `energy` | Oil & gas, utilities, renewables |

---

## Error Responses

All errors follow a consistent format:

```json
{ "detail": "Human-readable error message" }
```

| Status | Meaning |
|---|---|
| `401 Unauthorized` | Missing `X-API-Key` header |
| `403 Forbidden` | Invalid API key |
| `404 Not Found` | Role profile not found |
| `422 Unprocessable Entity` | Request validation failed |
| `500 Internal Server Error` | Unexpected server error |
