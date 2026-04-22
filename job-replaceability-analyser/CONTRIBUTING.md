# Contributing to Job Replaceability Analyser

Thank you for your interest in contributing. This project aims to provide honest, evidence-based analysis of AI's impact on cybersecurity roles — your contributions help keep it accurate and useful.

## Ways to Contribute

- **Add or improve role profiles** — JSON files under `data/roles/`
- **Improve scoring logic** — dimension scorers in `core/dimensions.py`
- **Add sector calibration data** — benchmarks under `data/benchmarks/`
- **Fix bugs or improve test coverage** — `tests/unit/` and `tests/integration/`
- **Improve documentation** — `docs/` directory

## Getting Started

```bash
git clone https://github.com/your-org/job-replaceability-analyser.git
cd job-replaceability-analyser
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pre-commit install
```

Run the test suite to verify your environment:

```bash
pytest
```

## Adding a Role Profile

Role profiles live in `data/roles/<slug>.json`. Use an existing profile (e.g. `soc_analyst_t1.json`) as a template. Required fields:

| Field | Type | Description |
|---|---|---|
| `canonical_name` | string | Display name |
| `family` | string | Role family (`blue_team`, `red_team`, `grc`, `engineering`, `leadership`) |
| `description` | string | One-sentence role description |
| `task_routineness_score` | 0–100 | Higher = more repetitive/rule-bound tasks |
| `data_dependency_score` | 0–100 | Higher = more reliance on structured data |
| `judgment_intensity_score` | 0–100 | Higher = more human judgment required |
| `social_adversarial_score` | 0–100 | Higher = more human/adversarial interaction |
| `tool_augmentation_ceiling_score` | 0–100 | Higher = more AI tooling already deployed |
| `high_risk_tasks` | list[string] | Tasks most exposed to automation |
| `low_risk_tasks` | list[string] | Tasks most resistant to automation |
| `recommended_skills` | list[string] | Upskilling recommendations |

Add an alias in `core/taxonomy.py` under `ROLE_ALIASES` so common synonyms resolve to your slug.

## Scoring Calibration

Dimension scores should be grounded in evidence, not intuition. When submitting a new profile, please include in your PR description:

- Sources used (industry reports, job postings, practitioner interviews)
- Comparison to the most similar existing profile and reasoning for differences
- Any specialisation overrides and their rationale

## Pull Request Guidelines

1. One profile or logical change per PR
2. All tests must pass: `pytest`
3. Lint must be clean: `ruff check .`
4. Include a brief description of what changed and why
5. For scoring changes that affect existing profiles, include a before/after comparison of affected scores

## Code of Conduct

Be respectful and constructive. This project discusses workforce displacement — a topic that affects real people's livelihoods. Contributions should reflect that seriousness.
