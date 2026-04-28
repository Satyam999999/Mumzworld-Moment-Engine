# Mumzworld Moment Engine — Architecture Tradeoffs

## Why This Problem Over the Listed Examples

- **Gift Finder**: listed, ~80% of applicants will attempt it, low retention impact
- **Product Comparison**: listed, content-generation heavy, doesn't drive repeat purchase
- **Moment Engine**: unlisted, maps directly to "follow a child's growth from pregnancy to pre-teen" JD language, retention impact is measurable (repeat purchase rate), harder to build correctly — the null path alone requires correct age math, milestone windows, confidence thresholds, and Pydantic validation of null fields

## Why Silence Is the Hardest Engineering Decision

Any system can recommend. Very few know when not to. The null path (`should_notify=False`) requires: correct age math, milestone window logic, confidence thresholds, and Pydantic validation enforcing null fields. Most demos skip the null path. We built and tested it explicitly — 6 of 15 evals test `should_notify=False`, and the Pydantic `model_validator` rejects empty strings (`""`) in place of null.

## Why Deterministic Milestone Calculation (Not LLM)

LLMs hallucinate age ranges. A model saying "babies start solids at 3 months" when medical consensus is 4–6 months is a liability on a children's platform. `milestone_calculator.py` is 100% deterministic, unit-testable, and auditable — the LLM only handles language, never facts.

## Architecture Choices

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Vector DB | FAISS flat index | 50 products fit in memory; no server overhead; 5-min setup. ChromaDB correct at 10k+ products |
| Reranker | TF-IDF cosine (fallback) | sentence-transformers / cross-encoder crashes on macOS 26 beta (PyTorch 2.7.1 mutex bug). TF-IDF preserves same 3-stage contract. Swap to cross-encoder when upstream fixes |
| Orchestration | LangGraph | Explicit state transitions, debuggable, easy to add human-review node for safety-critical recs |
| Inference | OpenRouter free tier | Sufficient for prototype; avoids paid key requirement; aligns with brief's free tooling encouragement |
| Arabic | Re-authoring, not translation | Gulf Arabic has warmth patterns not preserved by translation. System prompt iterates on register, pronoun ("طفلك" not "الطفل"), and ending style |

## What Was Cut

- **Real product images**: scraping forbidden; production uses Mumzworld CDN
- **Seasonal gating (MS-020 swimwear)**: requires current date + location; noted as next step
- **Push delivery (FCM/WhatsApp API)**: out of scope; `/notify-check` is the integration surface
- **Personalization beyond age**: purchase frequency, price sensitivity, brand affinity — requires behavioral data; architecture supports adding these as retrieval filters
- **Multiple children per account**: current schema assumes one child; production needs `child_profiles[]`

## Known Failure Modes (Honest)

| Failure | Impact | Fix |
|---------|--------|-----|
| Twin/multiple children | wrong milestone for second child | `child_profiles[]` array in schema |
| Premature babies | calendar age ≠ developmental age | gestational age adjustment field |
| Milestone clustering | 3 milestones in one window → only nearest fires | product decision, not a bug; log all in `sources[]` |
| Arabic quality bounded by model | Gulf nuance varies by checkpoint | human review before production |
| PyTorch on macOS 26 beta | sentence-transformers unavailable | fixed in next PyTorch release; TF-IDF fallback active |
| OpenRouter rate limits | free tier may throttle under load | add retry logic with exponential backoff |

## What's Next (Production Path)

1. Replace TF-IDF retriever with sentence-transformers once macOS 26 / PyTorch 2.8 fixes threading
2. Add `child_profiles[]` for multiple children per account
3. Add purchase frequency and price sensitivity as retrieval rerank signals
4. Add MS-020 seasonal gating (summer month detection by country)
5. Connect to FCM/WhatsApp for actual push delivery
6. Add human-review node in LangGraph for safety-flagged recommendations (allergy, choking hazard)
