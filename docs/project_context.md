# Grinta — Project Context

## Vision

Grinta is a football analytics reasoning engine that explains match outcomes using structured, evidence-based analysis.

It does not predict results.
It explains them.

The system must generate grounded, auditable explanations using only provided metrics.

---

## Core Principles

1. Evidence > Fluency
2. No hallucinated metrics
3. All claims must map to computed data
4. Uncertainty must be explicitly stated
5. Confidence must be calibrated

---

## Scope (Phase 1)

We are starting with TEAM-LEVEL explanations only.

Example questions:
- Why did Liverpool concede in the last 10 minutes?
- Why did Arsenal lose control after halftime?
- Why did Team X struggle to create chances?

We are NOT starting with:
- Player-level decline analysis
- Tactical formation inference
- Prediction models

---

## Architecture Overview

1. Ingest StatsBomb data
2. Compute structured team-level metrics
3. Construct a bounded reasoning input object
4. Pass structured input to LLM
5. Enforce JSON output schema
6. Display via Streamlit UI

---

## Folder Responsibilities

data/raw/         → raw StatsBomb JSON
data/processed/   → cleaned event-level data

ingestion/        → data loading + normalization
features/         → team-level metric computation
reasoning/        → schemas, contracts, system prompt
app/              → Streamlit UI

---

## Philosophy

The LLM is not allowed to:
- Fetch data
- Compute metrics
- Use external football knowledge

It only reasons over structured inputs.

The goal is disciplined, explainable AI.
