# Mumzworld Moment Engine — Complete Project Explanation
### Track A | Satyam Ghosh | IIITDM Jabalpur

---

## 1. THE IDEA — WHY THIS EXISTS

### The Problem Nobody Talks About

Mumzworld's retention problem is not acquisition. It is **silence**.

Picture this: A mother buys a newborn car seat in January. By July, her child
is 6 months old — rolling over, about to start solid foods, outgrowing the
bassinet. She needs 15 new products. She doesn't come back to Mumzworld —
not because she left — but because **nobody told her it was time**.

She Googled "when do babies start solids" and bought from wherever the top
result linked. Mumzworld lost that sale. And the next 14.

### The Insight

Most e-commerce recommendation systems answer the question:
> "What should I recommend right now?"

The Mumz Moment Engine asks a harder question:
> "Is this even the *right moment* to reach out — or should I stay silent?"

An AI that knows when to shut up is rarer and harder to build than one that
always talks. The null path — `should_notify: False` — is the engineering
insight. Most systems never build it.

### Why This Problem Was Chosen Over Listed Examples

The brief said: *"A well-defended novel problem beats a strong execution of a
listed one, every time."*

- Gift Finder, Product Comparison, Reviews Synthesizer — all listed → ~80% of
  applicants will attempt these
- Moment Engine — NOT listed → maps directly to the JD phrase "recommendation
  systems that follow a child's growth from pregnancy to pre-teen"
- Revenue impact is measurable — repeat purchase rate is the single hardest
  metric in e-commerce. One well-timed notification beats ten generic blasts.
- Emotionally resonant — the brief says "make a mother's life easier" three
  times. This does exactly that.

---

## 2. SYSTEM ARCHITECTURE — THE 5-LAYER PIPELINE

```
[TRIGGER]
customer_id (e.g. "C-001")
      │
      ▼
[LAYER 1] MILESTONE CALCULATOR (deterministic — zero LLM)
  • Load customer DOB from customers.json
  • Compute child_age_days = today − DOB
  • Scan milestone_rules.json for any milestone where:
      child_age_days ∈ [typical_age_days − 30, typical_age_days]
  • Compute confidence score:
      peak at 7 days before milestone (conf ≈ 1.0)
      lower at boundary (conf ≈ 0.5)
  • If confidence < 0.75 → STOP → return MomentBundle(should_notify=False)
  • Special paths: no DOB → conf=0.0 | age > 1825d → conf=0.0 | pregnant → MS-025
      │
      ▼ (only if milestone found with confidence ≥ 0.75)
[LAYER 2] PRODUCT RETRIEVER — TF-IDF FAISS + Hard Age Filter
  Stage 1: TF-IDF vectorizer encodes all 50 product descriptions
           FAISS IndexFlatIP finds top-10 semantically similar products
  Stage 2: Hard age filter — NON-NEGOTIABLE
           product.age_min_months ≤ child_age_months ≤ product.age_max_months
           If nothing passes → return [] (never hallucinate products)
  Stage 3: Cosine similarity rerank by milestone relevance
           Return top-3 age-verified, milestone-relevant products
      │
      ▼
[LAYER 3] PURCHASE HISTORY DEDUPLICATOR
  • Remove any retrieved product already in customer's purchase_history[]
  • Remove products listed in incompatible_with[] of any owned product
    (e.g. if she owns infant car seat MW-009, exclude forward-facing MW-010)
  • If all candidates removed → candidates = [] (but milestone still fires)
      │
      ▼
[LAYER 4] LANGGRAPH AGENT — 5-Node State Machine

  Node 1: route_node
    • confidence ≥ 0.75 AND milestone found → proceed to generate_en
    • else → set bundle(should_notify=False) → END immediately

  Node 2: generate_en_node
    • Build prompt with: customer name, child age, milestone, product catalog
    • Call Groq API (llama-3.3-70b-versatile)
    • Request: one EN notification ≤ 25 words + product reasoning dict
    • Rules: address by first name, no marketing speak, friend-like tone

  Node 3: translate_ar_node
    • Take EN copy → re-author in Gulf Arabic (NOT translate)
    • Use Gulf Arabic system prompt (عزيزتي, طفلك, ≤ 25 words, warm tone)
    • Rules: never "يا مستخدم", use milestone AR name, end with warmth

  Node 4: validate_node
    • Strip markdown fences from LLM response (_extract_json)
    • Parse into MomentBundle via Pydantic v2
    • If validation fails → log + return safe fallback(should_notify=False)
    • NEVER propagate validation error silently

  Node 5: format_node
    • Pass-through — bundle already assembled in validate_node
    • Attach sources[] (product IDs + rule IDs that grounded this output)
      │
      ▼
[LAYER 5] STRUCTURED OUTPUT — MomentBundle (Pydantic v2)
  {
    should_notify        : bool
    moment_name_en       : str | None
    moment_name_ar       : str | None
    notification_copy_en : str | None   ← ≤ 25 words, warm
    notification_copy_ar : str | None   ← Gulf Arabic, re-authored
    recommendations      : list[ProductRecommendation]
    reasoning            : str          ← ALWAYS present, even on null path
    sources              : list[str]    ← product IDs + rule IDs
    child_age_days       : int
    milestone_confidence : float
  }
```

---

## 3. DATA — WHAT WAS BUILT

### 3.1 milestone_rules.json — 25 Developmental Milestones

25 milestones covering the full child journey from pregnancy to age 5:

| ID | Milestone | Typical Age |
|----|-----------|-------------|
| MS-001 | Starting Solids | 180 days |
| MS-002 | Tummy Time / Rolling Over | 90 days |
| MS-004 | First Steps / Walking | 365 days |
| MS-010 | First Teeth / Teething Peak | 150 days |
| MS-012 | Potty Training Readiness | 540 days |
| MS-019 | First Shoes | 330 days |
| MS-021 | First Birthday Party Prep | 335 days |
| MS-025 | Pregnancy — Third Trimester Hospital Bag | 245 days |
| ... | 17 more milestones | ... |

Each milestone has: rule_id, name_en, name_ar, typical_age_days, window_days,
description, search_query, safety_note.

### 3.2 catalog.json — 50 Products

50 synthetic Mumzworld products across 9 categories:

| Category | Count | Examples |
|----------|-------|---------|
| Feeding/weaning | 8 | Chicco Weaning Set, NUK Sippy Cup |
| Car seats | 6 | Joie i-Spin 360, Graco 4Ever DLX |
| Strollers | 5 | Bugaboo Bee6, Maclaren Techno XT |
| Sleep | 5 | SNOO Smart Bassinet, Stokke Sleepi |
| Bath/grooming | 5 | Angelcare Bath Seat, Stokke Flexi Bath |
| Toys/development | 8 | Fisher-Price Tummy Time Mat, VTech Walker |
| Clothing/shoes | 4 | Stride Rite First Walkers, Carter's Set |
| Nursery/school bags | 4 | Skip Hop Zoo Backpack, JuJuBe Diaper Bag |
| Health/teething | 5 | Sophie La Girafe, NUK Teether Set |

Each product: product_id, bilingual names, age_min_months, age_max_months,
milestone_tags[], safety_certs[], incompatible_with[], price_aed, in_stock.

### 3.3 customers.json — 20 Profiles

20 synthetic customers designed to test all code paths:
- 10 Arabic-language (UAE, KSA, Kuwait)
- 10 English-language
- DOBs set to trigger different milestones across the 20 profiles
- 2 customers with NO child_dob (new accounts) → silent path
- 1 customer with 14-year-old child (aged out) → silent path
- 1 pregnant customer → MS-025 path
- 1 adversarial customer (owns all feeding products) → deduplicator test

---

## 4. TECHNICAL IMPLEMENTATION — FILE BY FILE

### src/schemas.py — Pydantic v2 Models

Three models with validation:

**MilestoneCheck**: Validates confidence ∈ [0, 1]. Cross-field validator: if
milestone_id is set, milestone_en and days_until_milestone must also be set.

**ProductRecommendation**: Captures product_id, bilingual names, price,
age_safety_verified flag, milestone_relevance string, retrieval_score.

**MomentBundle**: The critical model. model_validator enforces:
- If should_notify=True → EN copy, AR copy, and moment_name_en are required
- If should_notify=False → copies MUST be None (not ""), recs MUST be []
  This is what prevents the most common mistake in production AI systems:
  sending empty string instead of null.

### src/milestone_calculator.py — Zero LLM, Fully Deterministic

Why deterministic? LLMs hallucinate age ranges. A model saying "babies start
solids at 3 months" when medical consensus is 4–6 months is a liability on a
children's platform.

Logic:
1. If no DOB → return confidence=0.0 immediately
2. If child_age_days > 1825 (5 years) → aged out, return confidence=0.0
3. If child_age_days < 0 (pregnant) → check if due in ≤ 90 days → MS-025
4. Otherwise: scan all rules, find nearest milestone in [0, 30] day window
5. Confidence formula: peak=1.0 at 7 days before milestone, degrades at edges

### src/retriever.py — TF-IDF FAISS + Hard Age Filter

Architecture: The spec calls for sentence-transformers (all-MiniLM-L6-v2) +
cross-encoder reranker. On this host (macOS 26 Tahoe beta), PyTorch 2.7.1
crashes on import due to a known mutex threading bug. Solution: TF-IDF with
bigrams + FAISS IndexFlatIP, preserving the identical 3-stage retrieval contract.

Stage 1: TF-IDF vectorizer (ngram_range=(1,2), sublinear_tf=True) encodes all
         product descriptions → L2-normalized float32 matrix → FAISS flat index
Stage 2: Hard age filter. NOT a soft preference — a strict elimination. Any
         product outside age_min to age_max is removed regardless of relevance.
Stage 3: Cosine similarity rerank of age-filtered candidates by query.

### src/deduplicator.py — Never Recommend What She Owns

Two-rule filter:
1. If product_id in purchase_history → skip (already owns it)
2. If product_id in any owned product's incompatible_with[] → skip
   (e.g. if she has the infant rear-facing seat, skip the forward-facing)

This is what separates a thoughtful system from a naive demo. The deduplicator
runs after retrieval, before the agent — so the LLM never even sees products
she already owns.

### src/agent.py — LangGraph 5-Node State Machine

StateGraph with typed AgentState (TypedDict). Key design decisions:

**route_node**: The gate. Checks confidence < 0.75 → immediately sets bundle
and exits via conditional edge to END. The LLM is never called for silent cases.

**generate_en_node**: Builds a grounded prompt with actual catalog data (names,
descriptions, prices, age ranges). Explicit instruction: "do NOT invent product
names, prices, or features not in the catalog above."

**translate_ar_node**: Uses the Gulf Arabic system prompt verbatim from the
master plan. Key rules: طفلك not الطفل, عزيزتي not يا مستخدم, ≤ 25 words.
This is re-authoring, not translation — a critical distinction.

**validate_node**: Calls _extract_json() to strip markdown code fences (Groq
often wraps JSON in ```json ... ```). Then Pydantic parse. Any exception →
safe fallback. NEVER propagates errors silently.

**_call_groq()**: OpenAI-compatible REST call to api.groq.com. Handles timeout
(returns '{}' for fallback) and API errors explicitly.

### src/pipeline.py — Orchestrator

Single entry point. Loads all three components, runs them in sequence:
1. Look up customer (unknown ID → graceful null immediately)
2. Parse DOB → MilestoneCalculator.calculate()
3. If confidence ≥ 0.75 → retriever.search() → deduplicate()
4. Build AgentState → agent.invoke()
5. Return final_state['bundle']

### api/main.py — FastAPI

Two endpoints:
- POST /notify-check: takes customer_id, returns MomentBundle JSON
- GET /health: returns {"status": "ok"}
- GET /customers: lists all customer IDs and names

Middleware: X-Response-Time header on every response.

---

## 5. ARABIC QUALITY — THE DIFFERENTIATOR

The brief explicitly says "Arabic that reads like a literal translation" is BAD.
A recruiter at a MENA company will paste the Arabic into WhatsApp and read it.

### What Bad Arabic Looks Like
Input: "Layla, your baby is ready for solids!"
Bad literal translation: "ليلى، طفلك جاهز للأطعمة الصلبة!"
(Sounds robotic, formal, unnatural in Gulf context)

### What Good Gulf Arabic Looks Like
Re-authored: "عزيزتي ليلى، يبدو أن وقت الفطام اقترب لطفلك الصغير 🌿"
(Warm, personal, natural — reads like a message from a knowledgeable friend)

### System Prompt Rules (in translate_ar_node)
- "طفلك" (your child) — not "الطفل" (the child, impersonal)
- "عزيزتي" or first name — never "يا مستخدم" (never "dear user")
- "إتمام الشراء" for checkout — not anglicized
- ≤ 25 words — Gulf Arabic is warm but direct
- Do not end with sales CTA — end with warmth

---

## 6. EVALS — 15 TEST CASES ACROSS 3 GROUPS

### Easy Notify (Cases 1–5): Should fire notification
- C-001: Starting Solids (5 days away, Arabic customer)
- C-002: First Steps / Walking (7 days away)
- C-003: Teething Peak (7 days away)
- C-001: AR copy quality check (same customer, different assertion)
- C-005: First Shoes (nearest milestone at 330d, 5d away)

### Easy Silent (Cases 6–10): Should stay completely silent
- C-007: Dead zone (500d, no milestone in 30d window)
- C-011: Between milestones (50d, 40d to tummy time)
- C-009: Newborn (1d old, no false positive)
- C-020: 14yo aged out of catalog
- C-018: No DOB on file

### Adversarial (Cases 11–15): Edge cases that break naive systems
- C-012: Milestone real but ALL matching products already owned
- C-FAKE: Unknown customer ID
- C-013: Milestone exactly 3 days away (confidence boundary)
- C-014: Two milestones at same day (90d) — nearest scan wins
- C-019: Second no-DOB customer

### Actual Score: 30/30 — 15/15 PASS (with Groq API key)

The null-path cases (6–10, 15) pass deterministically — no LLM needed.
The notify cases pass with Groq llama-3.3-70b-versatile.

---

## 7. WHY THE SILENCE PATH IS THE HARDEST PART

Most AI demos only show the "happy path" — a query goes in, an answer comes out.

This system required building and testing the failure paths explicitly:
1. No DOB → confidence=0.0 → should_notify=False
2. Dead zone → no milestone in 30d window → should_notify=False
3. Aged out → child too old → should_notify=False
4. Validation error → safe fallback → should_notify=False
5. All products owned → notify of milestone, recommendations=[]
6. Out of stock → notify of milestone, recommendations=[]
7. Unknown customer → graceful null → no 500 error

The Pydantic model_validator on MomentBundle enforces null hygiene at the
schema level — making it structurally impossible to return empty string
instead of null, or a non-empty recommendations list on a silent path.

---

## 8. KEY TRADEOFFS MADE

| Decision | What | Why |
|----------|------|-----|
| TF-IDF over sentence-transformers | Using sklearn TF-IDF + FAISS instead of neural embeddings | PyTorch 2.7.1 crashes on macOS 26 beta due to mutex threading bug. TF-IDF preserves identical 3-stage retrieval contract. Swap when PyTorch fixes the issue. |
| Groq over OpenRouter | Free tier, fast, OpenAI-compatible | Lower latency, simpler auth, llama-3.3-70b-versatile is the same model class |
| LangGraph over raw chaining | Explicit state machine | Debuggable state transitions, easy to add human-review node later |
| FAISS flat over ChromaDB | In-memory flat index | 50 products fit trivially; no server overhead; 5-min setup |
| Deterministic age calc | No LLM for milestone timing | LLMs hallucinate developmental age ranges — unacceptable on a children's platform |
| Nearest milestone only | Single milestone per run | Product decision: one timely notification > multiple overwhelming ones |

---

## 9. WHAT'S NEXT (PRODUCTION PATH)

1. **Swap retriever**: sentence-transformers + cross-encoder when macOS 26 /
   PyTorch 2.8 fixes threading
2. **Multiple children**: Add `child_profiles[]` array to customer schema
3. **Gestational age**: Adjust milestone timing for premature babies
4. **Seasonal gating**: MS-020 (swimwear) gates on summer month + country
5. **Push delivery**: Connect to FCM or WhatsApp Business API
6. **Human review node**: Add LangGraph node for safety-flagged products
7. **Personalization signals**: Purchase frequency, price sensitivity, brand
   affinity as additional retrieval rerank factors

---

## 10. FILE MAP

```
mumzworld-moment-engine/
├── README.md                   ← submission doc
├── EVALS.md                    ← rubric + 15 cases + honest scores
├── TRADEOFFS.md                ← architecture decisions
├── PROJECT_EXPLANATION.md      ← this file
├── DEMO_SCRIPT.md              ← 3-min video script
├── requirements.txt
├── .env.example                ← GROQ_API_KEY=your_key_here
│
├── data/
│   ├── generate_data.py        ← generates all JSON files
│   ├── milestone_rules.json    ← 25 milestones
│   ├── catalog.json            ← 50 products
│   └── customers.json          ← 20 customer profiles
│
├── src/
│   ├── schemas.py              ← Pydantic v2: MilestoneCheck, ProductRec, MomentBundle
│   ├── milestone_calculator.py ← deterministic, zero LLM
│   ├── retriever.py            ← TF-IDF FAISS + hard age filter
│   ├── deduplicator.py         ← purchase history filter
│   ├── agent.py                ← LangGraph 5-node state machine
│   └── pipeline.py             ← orchestrator
│
├── api/
│   └── main.py                 ← FastAPI: POST /notify-check, GET /health
│
├── eval/
│   ├── test_cases.json         ← 15 test cases
│   ├── run_evals.py            ← rich score table
│   ├── generate_eval_csv.py    ← produces evaluation_results.csv
│   └── evaluation_results.csv  ← actual results (30/30)
│
└── demo/
    └── demo.py                 ← CLI: 5 Loom cases, rich terminal output
```
