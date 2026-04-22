# Scoring Methodology

## Overview

The Job Replaceability Analyser produces a **replaceability index** — a 0–100 score representing how exposed a given cybersecurity role is to displacement by AI and automation, at the time of analysis.

A score of 0 means the role is effectively immune to automation under any foreseeable near-term trajectory. A score of 100 would mean full automation is both technically feasible and actively deployed — in practice no role reaches this ceiling, and scores are capped at 95 in projections.

---

## Dimension Model

The index is a weighted composite of five dimensions. Each dimension is scored 0–100 for the role, then multiplied by its weight.

### 1. Task Routineness (weight: 0.20)

Measures how repetitive and rule-bound the role's core tasks are. Alert triage following a fixed playbook scores high; novel exploit development scores low.

**High score indicators:** Checklist-driven workflows, fixed escalation criteria, template-based outputs, pattern-matching on known signatures.

**Low score indicators:** Novel problem formulation, open-ended investigation, creative adversarial reasoning.

### 2. Data Dependency (weight: 0.20)

Measures whether the role's inputs are primarily structured, machine-readable data. SIEM analysts working with normalised log data score high; intelligence analysts synthesising human-sourced reporting score lower.

**High score indicators:** Structured telemetry, CVE databases, STIX feeds, binary file analysis, network packet capture.

**Low score indicators:** Stakeholder interviews, unstructured threat reports, social engineering, physical environment assessment.

### 3. Judgment Intensity (weight: 0.25)

Measures how much the role depends on contextual, ethical, or high-stakes reasoning that cannot be reduced to rules. This dimension is inverted in the composite: high judgment → lower replaceability.

**High judgment indicators:** Incident attribution, legal and regulatory interpretation, breach disclosure decisions, risk acceptance under uncertainty, strategic security programme design.

**Low judgment indicators:** Applying a defined playbook, running a scripted scan, producing a templated compliance report.

### 4. Social & Adversarial Complexity (weight: 0.20)

Measures the degree to which the role requires human interaction, negotiation, or creative adversarial thinking. Also inverted: high complexity → lower replaceability.

**High complexity indicators:** Red team campaign design, executive communication during crises, penetration test scoping negotiation, social engineering assessments, insider threat investigation.

**Low complexity indicators:** Autonomous log analysis, automated scanning pipelines, dashboard monitoring.

### 5. Tool Augmentation Ceiling (weight: 0.15)

Measures how much AI tooling is already deployed in this role area and how much further automation headroom exists. High ceiling → higher replaceability.

**High ceiling indicators:** Mature SOAR playbook automation, AI-assisted triage (e.g. Darktrace, Vectra), automated vulnerability scanners, LLM-assisted report drafting tools in active commercial deployment.

**Low ceiling indicators:** Novel attack surface types, adversarial ML, OT/ICS environments with limited tool support, highly contextual GRC work.

---

## Modifiers

After the weighted composite is computed, two modifiers are applied sequentially.

### Experience Modifier

Senior practitioners (8+ years) receive a mild downward adjustment (-4 to -8 points) reflecting insulation through specialisation, institutional knowledge, and leadership responsibilities. Very early-career practitioners (≤2 years) receive a small upward adjustment (+3 points) as their work skews toward automatable entry-level tasks.

### Sector Modifier

A sector multiplier (default 1.0) scales the index to reflect structural differences in AI adoption across industries. Technology sector organisations adopt automation faster (×1.10); government and defence organisations face procurement cycles, security clearance constraints, and regulatory friction that slow displacement (×0.85–0.90).

---

## Projection Model

The five-year projection uses a logistic growth curve:

```
projected(t) = 95 / (1 + ((95 - index) / index) × exp(-k × (t - lag)))
```

Where:
- `95` is the practical automation ceiling
- `k` is the AI capability growth rate (default 0.18 = 18% annually)
- `lag` is the adoption delay in years (default 1.5)
- `t` is years into the future

The logistic form reflects that automation adoption accelerates through a mid-range (the "S-curve" of technology deployment) before decelerating as hard-to-automate task residuals dominate. Projections never decrease below the current index.

---

## Risk Tiers

| Score | Tier | Interpretation |
|---|---|---|
| 0–25 | Very Low | Highly resistant to automation in the near term |
| 26–45 | Low | Some routine tasks automatable; core requires human expertise |
| 46–60 | Moderate | Significant task displacement expected; upskilling advisable |
| 61–75 | High | Most core tasks within reach of current or near-term AI tooling |
| 76–100 | Very High | Role likely to be substantially restructured or absorbed |

---

## Limitations and Caveats

**Scores are probabilistic, not predictive.** The trajectory of AI capability — particularly the speed of agentic and reasoning model deployment in security tooling — is genuinely uncertain.

**Role-level scores obscure individual variation.** A SOC Analyst Tier 1 who specialises in OT environments and threat hunting is more insulated than the role-level score implies. The analyser provides a baseline, not a verdict on any individual.

**Adversarial dynamics are hard to model.** AI-enabled attackers may increase demand for human defenders even as AI also augments defenders. This second-order effect is not captured in the current model.

**Regulatory lag is structural.** In highly regulated environments (government, healthcare, critical infrastructure), even technically feasible automation is slowed by procurement rules, compliance requirements, and accountability frameworks. The sector modifier partially captures this but cannot reflect jurisdiction-specific constraints.

**The model requires ongoing calibration.** AI capability is advancing rapidly. Dimension scores for specific roles should be reviewed annually against updated industry data.
