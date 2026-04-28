import json, os, httpx
from typing import TypedDict, Annotated
from src.schemas import MilestoneCheck, MomentBundle, ProductRecommendation
from langgraph.graph import StateGraph, END

GULF_ARABIC_SYSTEM = """You are a native Arabic copywriter writing short notifications for Gulf mothers
in the UAE, Saudi Arabia, and Kuwait. Your Arabic must:
- Sound like a knowledgeable, caring friend — not a push notification
- Use Modern Standard Arabic with Gulf warmth and directness
- Use "طفلك" (your child) — personal, not "الطفل" (the child) — distant
- Address her as "عزيزتي" or by first name, never "يا مستخدم"
- "إتمام الشراء" for checkout, "منتج" for product — never anglicized transliterations
- Keep it ≤ 25 words — Gulf Arabic is warm but direct, never wordy
- If mentioning a milestone, use the Arabic milestone name provided
- Do not end with a sales call-to-action — end with warmth"""

class AgentState(TypedDict):
    customer: dict
    milestone: MilestoneCheck
    candidates: list[dict]
    bundle: MomentBundle | None
    error: str | None
    _en_raw: str
    _ar_raw: str

# ── Node 1: route ──────────────────────────────────────────────────
def route_node(state: AgentState) -> AgentState:
    m = state['milestone']
    if m.confidence < 0.75:
        state['bundle'] = MomentBundle(
            should_notify=False, moment_name_en=None, moment_name_ar=None,
            notification_copy_en=None, notification_copy_ar=None,
            recommendations=[],
            reasoning=(f"Confidence {m.confidence:.2f} below threshold 0.75. "
                       f"Child age {m.child_age_days} days. "
                       f"No milestone imminent or insufficient certainty."),
            sources=[], child_age_days=m.child_age_days,
            milestone_confidence=m.confidence
        )
    return state

def should_continue(state: AgentState) -> str:
    return "end" if state.get('bundle') is not None else "generate_en"

# ── Node 2: generate_en ────────────────────────────────────────────
def generate_en_node(state: AgentState) -> AgentState:
    m = state['milestone']
    customer = state['customer']
    candidates = state['candidates']
    child_age_months = m.child_age_days // 30
    first_name = customer['name'].split()[0]

    product_context = json.dumps([{
        'product_id': p['product_id'], 'name': p['name_en'],
        'description': p['description_en'], 'price_aed': p['price_aed'],
        'age_range': f"{p['age_min_months']}–{p['age_max_months']} months"
    } for p in candidates], indent=2) if candidates else "No products available for this milestone."

    prompt = f"""You are writing a single warm notification for a mother on Mumzworld.

Customer name: {customer['name']} (use first name: {first_name})
Child age: {child_age_months} months ({m.child_age_days} days)
Upcoming milestone: {m.upcoming_milestone_en} (in {m.days_until_milestone} days)
Available products (age-verified, from catalog):
{product_context}

Write ONE English notification sentence (≤ 25 words). Rules:
- Address her by first name ({first_name})
- Mention the milestone specifically
- Sound like a knowledgeable friend, not a marketing email
- If no products available, mention the milestone only — do NOT invent products

Also write a one-sentence reasoning for each recommended product (why this product for this milestone).

Return ONLY valid JSON:
{{
  "notification_copy_en": "...",
  "product_reasonings": {{
    "MW-XXX": "one sentence grounded in catalog data"
  }}
}}

Do NOT invent product names, prices, or features not in the catalog above."""

    try:
        state['_en_raw'] = _call_openrouter(prompt)
    except Exception as e:
        print(f"[WARN] EN generation failed: {e}")
        state['_en_raw'] = '{}'
    return state

# ── Node 3: translate_ar ───────────────────────────────────────────
def translate_ar_node(state: AgentState) -> AgentState:
    try:
        en_data = json.loads(state.get('_en_raw', '{}'))
    except json.JSONDecodeError:
        en_data = {}
    en_copy = en_data.get('notification_copy_en', '')
    m = state['milestone']
    first_name = state['customer']['name'].split()[0]

    prompt = f"""{GULF_ARABIC_SYSTEM}

English notification: "{en_copy}"
Milestone in Arabic: {m.upcoming_milestone_ar}
Customer first name: {first_name}

Re-author this in Gulf Arabic. Do NOT translate literally — write it fresh in Arabic.
BAD: "ليلى، طفلك جاهز للأطعمة الصلبة!"
GOOD: "عزيزتي ليلى، يبدو أن وقت الفطام اقترب لطفلك الصغير 🌿"

Return ONLY valid JSON:
{{"notification_copy_ar": "..."}}"""

    try:
        state['_ar_raw'] = _call_openrouter(prompt)
    except Exception as e:
        print(f"[WARN] AR generation failed: {e}")
        state['_ar_raw'] = '{}'
    return state

# ── Node 4: validate ───────────────────────────────────────────────
def validate_node(state: AgentState) -> AgentState:
    try:
        try:
            en_data = json.loads(state.get('_en_raw', '{}'))
        except json.JSONDecodeError:
            en_data = {}
        try:
            ar_data = json.loads(state.get('_ar_raw', '{}'))
        except json.JSONDecodeError:
            ar_data = {}

        m = state['milestone']
        candidates = state['candidates']
        reasonings = en_data.get('product_reasonings', {})

        recs = []
        for p in candidates:
            pid = p['product_id']
            recs.append(ProductRecommendation(
                product_id=pid, name_en=p['name_en'], name_ar=p['name_ar'],
                price_aed=p['price_aed'], age_safety_verified=True,
                milestone_relevance=reasonings.get(pid, f"Relevant to {m.upcoming_milestone_en} milestone."),
                retrieval_score=p.get('_rerank_score', 0.0)
            ))

        en_copy = en_data.get('notification_copy_en')
        ar_copy = ar_data.get('notification_copy_ar')

        # Guard: must have both copies to notify
        if not en_copy or not ar_copy:
            raise ValueError(f"Missing copy: en={bool(en_copy)}, ar={bool(ar_copy)}")

        state['bundle'] = MomentBundle(
            should_notify=True,
            moment_name_en=m.upcoming_milestone_en,
            moment_name_ar=m.upcoming_milestone_ar,
            notification_copy_en=en_copy,
            notification_copy_ar=ar_copy,
            recommendations=recs,
            reasoning=(f"Milestone '{m.upcoming_milestone_en}' detected "
                       f"{m.days_until_milestone} days away. "
                       f"Confidence: {m.confidence:.2f}. "
                       f"{len(recs)} age-verified products retrieved."),
            sources=[p['product_id'] for p in candidates] + [m.upcoming_milestone_id],
            child_age_days=m.child_age_days,
            milestone_confidence=m.confidence
        )

    except Exception as e:
        print(f"[VALIDATION ERROR] {e}")
        state['bundle'] = MomentBundle(
            should_notify=False, moment_name_en=None, moment_name_ar=None,
            notification_copy_en=None, notification_copy_ar=None,
            recommendations=[],
            reasoning=f"Output validation failed: {str(e)}. Safe fallback applied.",
            sources=[], child_age_days=state['milestone'].child_age_days,
            milestone_confidence=0.0
        )
    return state

# ── Node 5: format (pass-through) ─────────────────────────────────
def format_node(state: AgentState) -> AgentState:
    return state

# ── Graph assembly ─────────────────────────────────────────────────
def build_agent():
    graph = StateGraph(AgentState)
    graph.add_node("route", route_node)
    graph.add_node("generate_en", generate_en_node)
    graph.add_node("translate_ar", translate_ar_node)
    graph.add_node("validate", validate_node)
    graph.add_node("format", format_node)

    graph.set_entry_point("route")
    graph.add_conditional_edges("route", should_continue, {
        "end": END, "generate_en": "generate_en"
    })
    graph.add_edge("generate_en", "translate_ar")
    graph.add_edge("translate_ar", "validate")
    graph.add_edge("validate", "format")
    graph.add_edge("format", END)
    return graph.compile()

# ── OpenRouter helper ──────────────────────────────────────────────
def _call_openrouter(prompt: str, model: str = "meta-llama/llama-3.3-70b-instruct:free") -> str:
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set")
    try:
        response = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://mumzworld-moment-engine.demo"
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 500
            },
            timeout=30.0
        )
        return response.json()['choices'][0]['message']['content']
    except httpx.TimeoutException:
        print("[WARN] OpenRouter timeout — returning empty JSON for fallback")
        return '{}'
    except Exception as e:
        print(f"[WARN] OpenRouter error: {e}")
        return '{}'
