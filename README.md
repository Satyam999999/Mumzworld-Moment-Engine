# Mumzworld Moment Engine
### Track A | Satyam Ghosh | IIITDM Jabalpur

> "Mumzworld's retention problem isn't acquisition — it's silence.
>  This agent breaks it at exactly the right moment."

---

## The Problem (Why This Matters)

Mumzworld's biggest retention problem is not acquisition — it is silence. A mother buys a newborn car seat. Six months pass. Her child is now rolling over, about to start solids, outgrowing the bassinet. She needs 15 new products. She does not come back — not because she left Mumzworld, but because nobody told her it was time.

The Mumz Moment Engine fixes this. It watches a child grow — day by day, from purchase history and date of birth — detects which developmental milestone is approaching in the next 30 days, and fires one warm, timely, hyper-personalized notification in the mother's language (English or Gulf Arabic) with exactly the products she needs. If no milestone is approaching, it stays completely silent. **An AI that knows when to shut up is rarer and harder to build than one that always talks.**

---

## System Architecture

```
TRIGGER: customer_id
    │
    ▼
MILESTONE CALCULATOR (deterministic — zero LLM)
  • computes child_age_days from DOB
  • scans milestone_rules.json for any milestone in [today, today+30]
  • returns MilestoneCheck(confidence, upcoming_milestone_id, days_until)
  • if confidence < 0.75 → STOP → MomentBundle(should_notify=False)
    │
    ▼ (only if milestone found)
PRODUCT RETRIEVER — TF-IDF FAISS + hard age filter + cosine rerank
  • Stage 1: TF-IDF FAISS semantic search (top-10)
  • Stage 2: hard age filter — age_min_months ≤ child_age ≤ age_max_months
  • Stage 3: cosine rerank by milestone relevance
  • if zero pass age filter → return [] (never hallucinate)
    │
    ▼
PURCHASE HISTORY DEDUPLICATOR
  • remove products already in purchase_history
  • remove products incompatible_with[] owned products
    │
    ▼
LANGGRAPH AGENT — 5-node state machine
  Node 1 route_node   → confidence gate (< 0.75 → END)
  Node 2 generate_en  → warm EN notification (≤ 25 words) via Groq
  Node 3 translate_ar → Gulf Arabic re-authoring (not translation)
  Node 4 validate     → Pydantic v2 parse + safe fallback on error
  Node 5 format       → assemble final MomentBundle
    │
    ▼
MomentBundle (Pydantic v2)
  should_notify, moment_name_en/ar, notification_copy_en/ar,
  recommendations[], reasoning, sources[], child_age_days, milestone_confidence
```

---

## Setup & Run (Under 5 Minutes)

```bash
git clone https://github.com/Satyam999999/mumzworld-moment-engine
cd mumzworld-moment-engine
pip install -r requirements.txt
cp .env.example .env
# Edit .env: add your GROQ_API_KEY (free at console.groq.com)
python data/generate_data.py              # generates all synthetic data
python -m uvicorn api.main:app --port 8000  # start API on :8000
python demo/demo.py                       # run 5 demo cases in terminal
python eval/run_evals.py                  # run 15 eval cases + score table
```

---

## Evals

Score: **28–29/30 points (14–15/15 PASS)** *(with valid Groq API key)*

Silent-path cases 6–10 and 15 pass deterministically (no LLM required). Notify cases require a valid Groq API key. ±1pt variance is due to LLM non-determinism on structured JSON output — the `_extract_json` helper mitigates but cannot fully eliminate it.

| Group | Cases | Result |
|-------|-------|--------|
| Easy notify (True) | 1–5 | 5/5 PASS |
| Easy silent (False) | 6–10 | 5/5 PASS (deterministic) |
| Adversarial | 11–15 | 4–5/5 PASS |

Full rubric, case breakdown, and honest failure analysis: [EVALS.md](EVALS.md)

---

## Arabic Quality

The system re-authors notifications in Gulf Arabic — not translates them.

| Milestone | EN | AR |
|-----------|----|----|
| Starting Solids (Aisha, 6mo) | "Aisha, your little one is probably ready for first foods — here's what Mumzworld moms love." | "عزيزتي عائشة، وقت الفطام اقترب لطفلتك الصغيرة 🌿 هذه المنتجات أكثر ما أحبته الأمهات." |
| First Steps (Sara, 12mo) | "Sara, first steps are just around the corner — time for proper first shoes and a safer space." | "قريباً ستمشي طفلتك يا سارة 👶 حان الوقت لأول حذاء ومساحة آمنة لها." |
| Teething (Hessa, 5mo) | "Hessa, teething usually starts around now — these picks will help both of you get through it." | "عزيزتي حصة، مرحلة التسنين على الأبواب 🌙 هذه المنتجات ستساعدك وطفلك." |

**System prompt rules (verbatim in `translate_ar_node`):**
- "طفلك" (your child), never "الطفل" (the child) — distant
- Address as "عزيزتي" or first name, never "يا مستخدم"
- "إتمام الشراء" for checkout — never anglicized transliterations
- ≤ 25 words — Gulf Arabic is warm but direct

---

## Tooling

| Tool | Version | Purpose |
|------|---------|---------|
| **Groq** + Llama 3.3 70B Versatile | free tier | EN notification copy + Gulf Arabic re-authoring |
| TF-IDF (sklearn) + FAISS | sklearn 1.4 / faiss-cpu | Product catalog embeddings + semantic retrieval + cosine rerank |
| LangGraph | latest | 5-node state machine with explicit silence path |
| FastAPI + Pydantic v2 | latest | API layer + schema validation on every LLM output |

---

## AI Usage Note

Used Claude (Antigravity) to scaffold `schemas.py`, `agent.py`, `retriever.py`, and data generation scripts. Wrote `milestone_calculator.py` deterministic logic manually — age math must not be LLM-generated or it is untestable. Iterated Arabic system prompt per Gulf Arabic quality guidelines. All 15 eval test cases written manually. The TF-IDF retriever fallback was designed manually after diagnosing the PyTorch 2.7.1 / macOS 26 threading incompatibility.

---

## Time Log

- Problem selection + architecture: 40 min
- Synthetic data generation (25 milestones + 50 products + 20 customers): 35 min
- Core pipeline (calculator + retriever + deduplicator): 2 hr
- LangGraph agent + Arabic system prompt: 1 hr
- Evals (writing + running + scoring): 45 min
- README + EVALS + TRADEOFFS: 45 min
- Debugging macOS 26 PyTorch threading: 30 min
- **Total: ~6.5 hr**

---

## One-Paragraph Summary

The Mumzworld Moment Engine is a life-stage aware notification agent that detects when a child is approaching a developmental milestone — starting solids, first steps, teething, car seat upgrade — and delivers one warm, timely, personalized notification to the mother in English or native Gulf Arabic, with age-verified product recommendations grounded in Mumzworld's catalog via RAG. When no milestone is approaching, the agent stays completely silent. It uses deterministic age calculation (no LLM for facts), TF-IDF FAISS retrieval with a hard age-safety filter, LangGraph for stateful orchestration with an explicit silence path, and Pydantic v2 schema validation on every LLM output. Every recommendation is grounded. Every uncertainty is explicit. The system knows when to talk and, more importantly, when not to.
