# Mumzworld Moment Engine
### Track A | Satyam Ghosh | IIITDM Jabalpur

---

## The Problem

Mumzworld's retention problem is not acquisition — it is silence.

A mother buys a newborn car seat. Six months later her child needs 15 new products. She doesn't come back — not because she left Mumzworld, but because nobody told her it was time.

The Moment Engine fixes this. It watches a child grow day by day, detects which developmental milestone is approaching in the next 30 days, and fires one warm, timely notification in the mother's language — English or native Gulf Arabic — with exactly the products she needs right now.

When nothing is approaching, **it stays silent. An AI that knows when not to talk is rarer and harder to build than one that always does.**

---

## Architecture

```
customer_id
    │
    ▼
MILESTONE CALCULATOR  (deterministic — zero LLM)
  · child_age_days from DOB
  · scan 25 milestone rules for upcoming window [0–30 days]
  · confidence < 0.75  →  STOP  →  MomentBundle(should_notify=False)
    │
    ▼  (milestone found, confidence ≥ 0.75)
PRODUCT RETRIEVER  (fastembed ONNX neural embeddings + FAISS + hard age filter)
  · top-10 semantic candidates via FAISS
  · hard age filter: age_min ≤ child_age ≤ age_max  [non-negotiable]
  · cosine rerank by milestone relevance
  · zero candidates after filter  →  return []  (never hallucinate)
    │
    ▼
DEDUPLICATOR
  · remove products in purchase_history
  · remove products incompatible with owned items
    │
    ▼
LANGGRAPH AGENT  (5-node state machine)
  route_node    →  confidence gate  (< 0.75 → END immediately)
  generate_en   →  EN copy ≤ 25 words via Groq (llama-3.3-70b-versatile)
  translate_ar  →  Gulf Arabic re-authoring  (not translation)
  validate      →  Pydantic v2 parse + safe fallback on any error
  format        →  assemble final MomentBundle
    │
    ▼
MomentBundle  (Pydantic v2 — null hygiene enforced at schema level)
  should_notify · moment_name_en/ar · notification_copy_en/ar
  recommendations[] · reasoning · sources[] · milestone_confidence
```

---

## Quickstart

```bash
git clone https://github.com/Satyam999999/Mumzworld-Moment-Engine
cd mumzworld-moment-engine
pip install -r requirements.txt
cp .env.example .env          # add GROQ_API_KEY (free at console.groq.com)
python data/generate_data.py  # 25 milestones · 50 products · 20 customers
python -m uvicorn api.main:app --port 8000
```

```bash
# Notify path (C-001 — Fatima, Starting Solids, Arabic)
curl -s -X POST http://localhost:8000/notify-check \
  -H "Content-Type: application/json" -d '{"customer_id": "C-001"}' | \
  python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin), ensure_ascii=False, indent=2))"

# Silent path (C-007 — dead zone, no milestone)
curl -s -X POST http://localhost:8000/notify-check \
  -H "Content-Type: application/json" -d '{"customer_id": "C-007"}' | \
  python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin), ensure_ascii=False, indent=2))"
```

---

## Evals

**Score: 30/30 (15/15 PASS)**

Silent-path cases 6–10 and 15 pass deterministically — no LLM needed.
Notify cases require a valid Groq key. The `_extract_json` helper strips markdown code fences from Groq responses before parsing, making JSON extraction robust.

| Group | Cases | Score |
|-------|-------|-------|
| Easy notify | 1–5 | 5/5 |
| Easy silent | 6–10 | 5/5 (deterministic) |
| Adversarial | 11–15 | 5/5 |

```bash
python eval/run_evals.py   # rich score table, 15 cases live
```

Full rubric + honest failure analysis: [EVALS.md](EVALS.md)

---

## Arabic Quality

The system **re-authors** notifications in Gulf Arabic — it does not translate.

| | EN | AR |
|-|----|-----|
| Starting Solids | *"Fatima, starting solids in 5 days!"* | *"عزيزتي فاطمة، يبدو أن وقت بداية الأكل الصلب اقترب لطفلك 🌿"* |
| First Steps | *"Sara, first steps are just around the corner."* | *"قريباً ستمشي طفلتك يا سارة 👶 حان الوقت لأول حذاء."* |

System prompt rules enforced in `translate_ar_node`:
- `طفلك` (your child) — never `الطفل` (the child, impersonal)
- `عزيزتي` or first name — never `يا مستخدم`
- ≤ 25 words — Gulf Arabic is warm but direct
- Re-authored from scratch, not machine-translated

---

## Tooling

| Tool | Purpose |
|------|---------|
| **Groq** · llama-3.3-70b-versatile (free) | EN copy generation + Gulf Arabic re-authoring |
| **fastembed** · BAAI/bge-small-en-v1.5 (ONNX) + FAISS | Neural sentence embeddings + semantic retrieval + cosine rerank |
| **LangGraph** | 5-node state machine with explicit silence path |
| **FastAPI + Pydantic v2** | API layer + schema-level null enforcement |
| **Claude (Antigravity / Google DeepMind)** | Scaffolded `schemas.py`, `agent.py`, `retriever.py`, data generation scripts. Milestone calculator deterministic logic written manually — age math must not be LLM-generated. Arabic system prompt iterated manually per Gulf Arabic quality guidelines. All 15 eval cases written manually. |

---

## Why This Problem

Most applicants build Gift Finder or Product Comparison — both listed in the brief. This system is unlisted, maps directly to the JD language ("recommendation systems that follow a child's growth from pregnancy to pre-teen"), and solves the hardest retention metric: **repeat purchase rate**.

The engineering insight isn't the notify path. It's the silence path — the confidence threshold, the deterministic age math, the Pydantic `model_validator` that makes empty-string-instead-of-null structurally impossible. Six of fifteen evals test exactly this.
