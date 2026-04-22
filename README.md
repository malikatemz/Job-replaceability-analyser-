# Job Replaceability Analyser
### Cybersecurity · AI & Automation · Workforce Intelligence

> Assess how vulnerable cybersecurity roles are to replacement by AI and automation — with evidence-based scoring, skill gap mapping, and strategic career guidance.

---

## Overview

The **Job Replaceability Analyser** is a workforce intelligence tool built for the cybersecurity domain. It evaluates specific job roles — from SOC analysts to penetration testers — against a structured model of AI/automation capability, producing a replaceability score alongside actionable insights for individuals, teams, and organisations.

As AI-driven tools increasingly handle threat detection, log analysis, vulnerability scanning, and incident triage, the nature of cybersecurity work is shifting. This project quantifies that shift and helps practitioners adapt.

---

## Features

- **Role scoring engine** — Produces a 0–100 replaceability index for any cybersecurity job title, broken down by task category
- **Skill gap mapper** — Identifies which skills within a role are most exposed to automation vs. those requiring human judgment
- **Trend projection** — Models replaceability change over 1, 3, and 5-year horizons based on current AI capability trajectories
- **Career path advisor** — Suggests lateral moves, upskilling paths, and hybrid human-AI roles with lower displacement risk
- **Organisational risk dashboard** — Aggregates individual role scores across teams to surface structural vulnerability
- **Audit trail** — Every score is traceable to source reasoning, enabling review and challenge

---

## Methodology

Replaceability is scored across five dimensions:

| Dimension | Description |
|---|---|
| **Task routineness** | How repetitive and rule-bound the role's core tasks are |
| **Data dependency** | Whether the role operates primarily on structured, machine-readable data |
| **Judgment intensity** | Degree to which decisions require contextual reasoning and ethical weight |
| **Social & adversarial complexity** | Human interaction, negotiation, red-teaming creativity, and novel threat response |
| **Tool augmentation ceiling** | How much AI tooling is already deployed — and how much headroom remains |

Each dimension is scored independently and combined using a weighted model calibrated against industry data. Weights are configurable per sector and organisation type.

---

## Scope: Cybersecurity Roles Covered

The analyser currently supports the following role families:

**Defensive / Blue Team**
- SOC Analyst (Tier 1–3)
- Threat Intelligence Analyst
- Incident Responder
- Security Operations Manager
- SIEM Engineer

**Offensive / Red Team**
- Penetration Tester (Web, Network, Cloud)
- Red Team Operator
- Bug Bounty Researcher
- Exploit Developer

**Governance, Risk & Compliance**
- CISO / Security Director
- GRC Analyst
- Auditor / Assessor
- Policy & Awareness Specialist

**Engineering & Architecture**
- Security Engineer
- Cloud Security Architect
- DevSecOps Engineer
- Identity & Access Management Specialist

**Emerging & Hybrid**
- AI Security Researcher
- Adversarial ML Specialist
- Cyber-Physical / OT Security Engineer

---

## Project Structure

```
job-replaceability-analyser/
│
├── core/
│   ├── scorer.py              # Role scoring engine
│   ├── dimensions.py          # Scoring dimension definitions and weights
│   ├── projections.py         # Trend and timeline modelling
│   └── taxonomy.py            # Cybersecurity role taxonomy
│
├── data/
│   ├── roles/                 # Role profiles (JSON)
│   ├── benchmarks/            # Industry benchmarks and calibration data
│   └── skills/                # Skill ontology for cybersecurity
│
├── api/
│   ├── routes.py              # REST API endpoints
│   ├── schemas.py             # Request/response schemas
│   └── auth.py                # Authentication middleware
│
├── dashboard/
│   ├── src/                   # Frontend source (React)
│   └── public/                # Static assets
│
├── reports/
│   └── templates/             # PDF and markdown report templates
│
├── tests/
│   ├── unit/
│   └── integration/
│
├── docs/
│   ├── methodology.md
│   ├── api-reference.md
│   └── role-profiles.md
│
├── config/
│   └── settings.yaml
│
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+ (for the dashboard)
- PostgreSQL 15+ (for persistent storage)
- An Anthropic API key (used for natural language role descriptions and career advice generation)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/job-replaceability-analyser.git
cd job-replaceability-analyser

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install dashboard dependencies
cd dashboard && npm install && cd ..

# Configure environment variables
cp .env.example .env
# Edit .env with your database credentials and API keys
```

### Running the API

```bash
uvicorn api.routes:app --reload --host 0.0.0.0 --port 8000
```

### Running the Dashboard

```bash
cd dashboard
npm run dev
```

### Running a Quick Analysis

```bash
python -m core.scorer --role "SOC Analyst Tier 1" --output report.json
```

---

## API Reference

### `POST /analyse`

Analyse a single role.

**Request**
```json
{
  "role": "Penetration Tester",
  "specialisation": "cloud",
  "experience_years": 4,
  "sector": "financial_services"
}
```

**Response**
```json
{
  "role": "Penetration Tester",
  "replaceability_index": 28,
  "risk_tier": "low",
  "dimensions": {
    "task_routineness": 22,
    "data_dependency": 35,
    "judgment_intensity": 18,
    "social_adversarial_complexity": 15,
    "tool_augmentation_ceiling": 40
  },
  "projection": {
    "year_1": 30,
    "year_3": 38,
    "year_5": 47
  },
  "high_risk_tasks": ["automated scanning", "report generation"],
  "low_risk_tasks": ["threat modelling", "novel exploit research", "client communication"],
  "recommended_skills": ["adversarial AI", "cloud-native security", "red team leadership"]
}
```

### `POST /analyse/team`

Analyse a full team of roles and return an aggregated risk profile.

### `GET /roles`

List all supported role profiles.

### `GET /roles/{role_id}`

Retrieve the full profile and task breakdown for a specific role.

Full API documentation is available at `/docs` when the server is running (Swagger UI).

---

## Configuration

Key settings in `config/settings.yaml`:

```yaml
scoring:
  model_version: "2.1"
  dimension_weights:
    task_routineness: 0.20
    data_dependency: 0.20
    judgment_intensity: 0.25
    social_adversarial_complexity: 0.20
    tool_augmentation_ceiling: 0.15
  sector_modifiers:
    financial_services: 1.05
    government: 0.90
    healthcare: 0.95
    technology: 1.10

projection:
  ai_capability_growth_rate: 0.18   # Annual compound growth estimate
  adoption_lag_years: 1.5

reporting:
  default_format: "json"            # json | pdf | markdown
  include_reasoning: true
```

---

## Data Sources & Calibration

The scoring model is calibrated against:

- NIST NICE Cybersecurity Workforce Framework task library
- ENISA Threat Landscape reports (2021–2024)
- Industry salary and demand surveys (ISC², SANS, LinkedIn)
- Published AI capability assessments for security tooling (Darktrace, CrowdStrike, Microsoft Security Copilot, etc.)
- Primary research: structured interviews with 40+ cybersecurity practitioners

Calibration data is versioned under `data/benchmarks/`. Contributions and corrections are welcome via pull request.

---

## Interpreting Scores

| Score | Risk Tier | Interpretation |
|---|---|---|
| 0–25 | **Very Low** | Role relies heavily on human creativity, judgment, and adversarial thinking — highly resistant to automation in the near term |
| 26–45 | **Low** | Some routine tasks are automatable, but the core of the role requires human expertise |
| 46–60 | **Moderate** | Significant task displacement expected; upskilling into higher-judgment areas is advisable |
| 61–75 | **High** | Most core tasks are within reach of current or near-term AI tooling |
| 76–100 | **Very High** | Role as currently defined is likely to be substantially restructured or absorbed |

Scores above 60 do not mean a role disappears — they mean the nature of the work and the skills required will change substantially within the projection window.

---

## Limitations

- Scores represent probabilistic assessments, not forecasts. The trajectory of AI in cybersecurity is uncertain.
- Replaceability is assessed at the role level. Individual practitioners in high-scoring roles may be insulated through specialisation, seniority, or institutional context.
- The model does not account for regulatory or policy constraints that may slow automation adoption in specific jurisdictions.
- Adversarial dynamics in cybersecurity (AI attackers vs. AI defenders) may accelerate or dampen displacement in ways that are difficult to model.

---

## Contributing

Contributions are welcome. Please read `CONTRIBUTING.md` before opening a pull request.

Areas where help is most needed:

- Additional role profiles, especially for OT/ICS and embedded systems security
- Sector-specific calibration data
- Non-English role taxonomy support
- Validation studies comparing score predictions to observed workforce changes

---

## Licence

MIT Licence. See `LICENSE` for details.

---

## Acknowledgements

Built with contributions from cybersecurity practitioners, workforce researchers, and AI policy analysts. Special thanks to the open-source communities behind FastAPI, Pydantic, React, and the NIST NICE Framework team.

---

*This project does not advocate for or against workforce automation. Its purpose is to provide honest, evidence-based analysis so that individuals and organisations can make informed decisions.*
