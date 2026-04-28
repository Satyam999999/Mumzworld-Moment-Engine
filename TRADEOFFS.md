# Architecture Tradeoffs

## Why This Problem

The brief listed Gift Finder, Product Comparison, and Reviews Synthesizer. This system builds none of them.

The Moment Engine is unlisted because it's harder: it requires getting the *timing* right, not just the content. A recommendation at the wrong moment is noise. A recommendation at exactly the right moment is retention. The JD phrase "recommendation systems that follow a child's growth from pregnancy to pre-teen" describes this system exactly.

The engineering differentiator isn't the notify path — it's the silence path. Six of fifteen evals test `should_notify: False`. Most AI demos never build it.

---

## Core Design Decisions

### 1. Deterministic age math — zero LLM for facts

The milestone calculator uses pure date arithmetic. No LLM is ever called to determine a child's developmental stage.

Why: LLMs hallucinate developmental age ranges. A model saying "babies start solids at 3 months" when medical consensus is 4–6 months is a liability on a children's platform. Age math is testable, auditable, and deterministic. The LLM handles language only.

### 2. Hard age filter before the LLM sees any product

The retriever enforces `age_min_months ≤ child_age ≤ age_max_months` as a structural gate — not a soft preference. Products that fail this filter never reach the agent. A product recommended to a child outside its age range is a safety issue, not a ranking error.

### 3. LangGraph state machine over a simple chain

LangGraph makes state transitions explicit and debuggable. The `route_node` exits to `END` before calling Groq for all silent cases — the LLM is never called when there's nothing to say. A simple chain would have to handle this with if-statements scattered across the code. A state machine makes the silence path a first-class architectural construct.

### 4. Pydantic v2 model_validator for null hygiene

The `MomentBundle` validator rejects any output where `should_notify=False` but `notification_copy_en` is an empty string instead of `None`. This is the most common failure mode in production notification systems — sending a blank push notification because the LLM returned `""` instead of `null`. Enforcing it at the schema level makes it structurally impossible.

### 5. TF-IDF FAISS over a vector database

50 products fit in memory. FAISS IndexFlatIP gives sub-millisecond retrieval with no server overhead. ChromaDB or Pinecone would be correct at 10,000+ products. At this catalog size they add complexity without benefit.

The spec called for sentence-transformers + cross-encoder reranking. PyTorch 2.7.1 on macOS 26 (Tahoe beta) crashes on import due to a threading bug in the C++ multiprocessing layer. TF-IDF with bigrams + cosine rerank preserves the identical three-stage retrieval contract. The retriever API is unchanged — swap in sentence-transformers when the upstream fix ships.

### 6. Groq over self-hosted or OpenAI

Free tier, 500 tokens/s, OpenAI-compatible API. No billing setup required for evaluation. The `_call_groq` helper is a single function — swapping to any OpenAI-compatible endpoint (OpenRouter, Azure, local Ollama) is a one-line change.

### 7. Re-authoring Arabic, not translating it

The `translate_ar_node` system prompt instructs the model to write Gulf Arabic from scratch given the milestone and customer context — not to translate the English copy word for word. Literal translation produces Arabic that reads like a foreign-language label. Gulf Arabic has warmth patterns, pronoun choices (`طفلك` vs `الطفل`), and address conventions (`عزيزتي`) that only emerge from re-authoring with context.

---

## What's Not Built (and Why)

| Feature | Why deferred |
|---------|--------------|
| Push delivery (FCM / WhatsApp) | Out of scope — `/notify-check` is the integration surface for any push layer |
| Multiple children per account | `child_profiles[]` array is the schema extension; single-child first |
| Seasonal gating (MS-020 swimwear) | Requires country + month lookup; straightforward to add |
| Personalization beyond age | Purchase frequency, brand affinity — requires behavioral data not in brief |

These are deferred, not forgotten. The architecture supports all of them as retrieval rerank signals or additional state machine nodes.
