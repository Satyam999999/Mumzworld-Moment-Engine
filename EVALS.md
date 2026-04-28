# Mumzworld Moment Engine — EVALS

## Scoring Rubric

| Score | Criteria |
|-------|----------|
| **PASS (2pts)** | Correct `should_notify` + valid JSON + Arabic present when notifying |
| **PARTIAL (1pt)** | Correct decision but weak reasoning or missing/poor Arabic |
| **FAIL (0pts)** | Wrong decision, hallucinated product, empty-string fields, crash |

---

## Results

> **Score: 30/30 points (15/15 PASS)**

| Case | Group | Description | Expected | Got | Result | Notes |
|------|-------|-------------|----------|-----|--------|-------|
| 1 | easy_notify | C-001 ~175d → Starting Solids | True | True | **PASS** | EN + AR ✓, 3 recs ✓ |
| 2 | easy_notify | C-002 ~358d → First Steps | True | True | **PASS** | EN + AR ✓ |
| 3 | easy_notify | C-003 ~143d → Teething Peak | True | True | **PASS** | EN + AR ✓ |
| 4 | easy_notify | C-001 Arabic copy natural | True | True | **PASS** | AR reads natively ✓ |
| 5 | easy_notify | C-005 ~325d → First Shoes (nearest, 330d) | True | True | **PASS** | nearest-wins logic ✓ |
| 6 | easy_silent | C-007 dead zone (~500d) | False | False | **PASS** | null fields ✓, recs=[] ✓ |
| 7 | easy_silent | C-011 between milestones (~50d) | False | False | **PASS** | null fields ✓ |
| 8 | easy_silent | C-009 newborn (~1d) | False | False | **PASS** | no false positive ✓ |
| 9 | easy_silent | C-020 14yo aged out | False | False | **PASS** | aged_out path ✓ |
| 10 | easy_silent | C-018 no DOB | False | False | **PASS** | confidence=0.0 ✓ |
| 11 | adversarial | C-012 all products owned | True | True | **PASS** | notify ✓, deduplicator ✓ |
| 12 | adversarial | C-FAKE unknown ID | False | False | **PASS** | graceful null ✓, no 500 ✓ |
| 13 | adversarial | C-013 confidence boundary (3d) | True | True | **PASS** | conf=0.87 > 0.75 ✓ |
| 14 | adversarial | Two milestones at 90d → nearest wins | True | True | **PASS** | MS-002 wins (nearest) ✓ |
| 15 | adversarial | C-019 no DOB (second) | False | False | **PASS** | null path ✓ |

---

## Null-Path Hygiene (Enforced at Schema Level)

All `should_notify=False` outputs verified:
- `notification_copy_en: null` — not `""` ← Pydantic `model_validator` blocks empty string
- `notification_copy_ar: null` — not `""`
- `recommendations: []` — empty list, never null

---

## Case 5 — Design Validation

C-005 (DOB = today − 325 days). Two milestones in the 30-day window:
- MS-019 First Shoes at 330d — **5 days away**
- MS-021 First Birthday at 335d — 10 days away

The calculator selects the nearest milestone (First Shoes) so the notification arrives at maximum relevance. This is the intended "nearest wins" behavior, confirmed deterministic. Case 5 validates exactly this edge: when two milestones are both in window, the closer one takes priority.

---

## What Makes This Hard to Score 30/30

Cases 6–10 and 15 (silent path) pass deterministically with zero LLM calls.
Cases 1–5, 11–14 (notify path) require the full pipeline:

1. **Milestone calculator** must detect the window correctly
2. **Retriever** must return age-safe products (hard filter enforced)
3. **Deduplicator** must remove owned products (case 11 edge case)
4. **Groq** must return valid JSON (the `_extract_json` helper strips markdown fences)
5. **Pydantic v2** must accept the assembled bundle (validator rejects malformed output)
6. **Arabic re-authoring** must produce non-null Gulf Arabic copy

All six must succeed. A single failure anywhere falls back to `should_notify=False` via the validate_node safe fallback.
