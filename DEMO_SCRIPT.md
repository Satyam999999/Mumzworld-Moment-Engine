# Mumzworld Moment Engine — 3-Minute Demo Script
### Track A | Satyam Ghosh | IIITDM Jabalpur

---

## SETUP BEFORE RECORDING

```bash
# Terminal 1 — start the API server
cd mumzworld-moment-engine
uvicorn api.main:app --reload

# Terminal 2 — ready for curl commands
cd mumzworld-moment-engine
```

**Screen layout:** Split terminal — API server logs on left (small), demo
terminal on right (large). Make font size 18+. Use a dark theme (Dracula,
One Dark). Turn off notifications.

---

## SEGMENT 1 — THE PROBLEM (0:00–0:30)

**[Camera: face / screen-share with slide or just text in terminal]**

*Speak slowly, confidently:*

> "Mumzworld's retention problem isn't acquisition — it's silence.
>
> A mother buys a newborn car seat. Six months later, her child needs 15 new
> products. She doesn't come back — not because she left Mumzworld — but
> because nobody told her it was time.
>
> I built the Mumz Moment Engine. It watches a child grow day by day, detects
> which developmental milestone is approaching in the next 30 days, and fires
> one warm, timely, personalized notification — in English or native Gulf Arabic —
> with exactly the products she needs.
>
> And when nothing is approaching? It stays completely silent.
> An AI that knows when to shut up is harder to build than one that always talks."

---

## SEGMENT 2 — QUICK ARCHITECTURE (0:30–0:50)

**[Screen: open src/pipeline.py or show architecture ASCII from README]**

*Type this in terminal or just speak while scrolling:*

```bash
cat README.md | head -60
```

> "Five layers: deterministic milestone calculator — zero LLM, fully testable
> age math. FAISS product retriever with a hard age filter — if a product isn't
> age-appropriate, it never reaches the LLM. A purchase deduplicator. A LangGraph
> 5-node state machine. And Pydantic v2 validation on every LLM output.
>
> The age calculation is deterministic by design — LLMs hallucinate developmental
> ages. That's unacceptable on a children's platform."

---

## SEGMENT 3 — CASE 1: THE MONEY CASE — NOTIFY + ARABIC (0:50–1:20)

**[Screen: terminal, large font]**

*Type this live:*

```bash
curl -s -X POST http://localhost:8000/notify-check \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "C-001"}' | python -m json.tool
```

*Wait for response (~3 seconds). Then narrate while pointing to output:*

> "C-001 is Fatima Al-Rashid — Arabic-language customer, child 175 days old.
> The system detected 'Starting Solids' is 5 days away — confidence 0.93.
>
> should_notify is True.
>
> Here's the English copy: [read it]. Under 25 words. Warm, personal.
>
> Now here's the Arabic: [read Arabic or spell out first word 'عزيزتي'].
> This is NOT a translation. This was re-authored in Gulf Arabic — 'عزيزتي فاطمة'
> means 'dear Fatima'. 'طفلك' means 'your child' — personal. 'الطفل' would mean
> 'the child' — distant. That's the difference between good Arabic and bad Arabic.
>
> Three product recommendations — all age-verified. You can see product IDs in
> the sources array. Every recommendation is grounded."

---

## SEGMENT 4 — CASE 2: SILENCE IS CORRECT (1:20–1:45)

**[Screen: terminal]**

```bash
curl -s -X POST http://localhost:8000/notify-check \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "C-007"}' | python -m json.tool
```

*Narrate while output appears:*

> "C-007's child is 500 days old — sitting in a dead zone between milestones.
>
> should_notify is False.
>
> Notice: notification_copy_en is **null** — not empty string. notification_copy_ar
> is **null**. recommendations is an **empty array**.
>
> Most AI systems return empty strings here. The Pydantic model_validator makes
> that structurally impossible — it rejects empty strings at the schema level.
>
> The reasoning field explains exactly why: 'Confidence 0.00 below threshold 0.75.
> No milestone imminent.' Explicit uncertainty, always present, even on the null path."

---

## SEGMENT 5 — CASE 3: ADVERSARIAL — ALL PRODUCTS OWNED (1:45–2:05)

**[Screen: terminal]**

```bash
curl -s -X POST http://localhost:8000/notify-check \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "C-012"}' | python -m json.tool
```

> "C-012 is another customer at the Starting Solids milestone — but she already
> owns all 7 feeding products in the catalog.
>
> The deduplicator removes everything she owns. Watch what happens:
>
> should_notify is **True** — because the milestone is real. She still needs to
> know it's time.
>
> But recommendations contains only non-feeding products — bath, health items
> that are age-appropriate but not already owned.
>
> The system did not hallucinate new feeding products. It did not pretend she
> doesn't own them. It told her about the milestone and was honest about what
> was left to recommend."

---

## SEGMENT 6 — CASE 4: NO DOB + UNKNOWN ID (2:05–2:25)

**[Screen: terminal — run both quickly]**

```bash
# New account — no DOB
curl -s -X POST http://localhost:8000/notify-check \
  -d '{"customer_id": "C-018"}' -H "Content-Type: application/json" | python -m json.tool
```

> "New customer — no date of birth on file. should_notify is False. Reasoning:
> confidence 0.0. The system refuses to guess. No hallucinated milestone."

```bash
# Unknown customer
curl -s -X POST http://localhost:8000/notify-check \
  -d '{"customer_id": "C-FAKE"}' -H "Content-Type: application/json" | python -m json.tool
```

> "Completely unknown ID. Graceful MomentBundle with should_notify False.
> No 500 error. No stack trace. The API stays stable."

---

## SEGMENT 7 — EVALS (2:25–2:45)

**[Screen: terminal]**

```bash
python eval/run_evals.py
```

*While table prints:*

> "15 test cases — easy notify, easy silent, and adversarial. The table scores
> each one live. [pause for table to finish]
>
> 30 out of 30 points. 15 of 15 pass. Including 6 cases specifically designed
> to test the silence path — because a system that only tests happy paths is
> not production-ready."

---

## SEGMENT 8 — CLOSE (2:45–3:00)

**[Camera: face or simple text card]**

> "The hardest part of this system wasn't making it talk.
>
> It was making it know when not to.
>
> The null path — the deterministic age math, the confidence threshold, the
> Pydantic null enforcement — that's the engineering insight. Most demos skip it.
>
> This one was built and tested explicitly, with 6 of 15 evals dedicated to it.
>
> Mumzworld Moment Engine. I'm Satyam Ghosh, IIITDM Jabalpur. Track A."

---

## TIMING GUIDE

| Segment | Duration | Cumulative |
|---------|----------|------------|
| 1 — The Problem | 30s | 0:30 |
| 2 — Architecture | 20s | 0:50 |
| 3 — Notify + Arabic | 30s | 1:20 |
| 4 — Silence correct | 25s | 1:45 |
| 5 — Adversarial | 20s | 2:05 |
| 6 — No DOB + Unknown ID | 20s | 2:25 |
| 7 — Evals | 20s | 2:45 |
| 8 — Close | 15s | 3:00 |

---

## RECORDING TIPS

1. **Rehearse segments 3–6 three times** — the curl commands must be typed
   without mistakes. Alternatively, put them in a shell script and run with one command.

2. **Pre-warm the API** — run one curl request before recording so the pipeline
   and retriever index are loaded. First call is always slower (FAISS build).

3. **Font size 18 minimum** — recruiters will watch on a small browser window.

4. **Speak slower than you think** — target 120 words/minute. Most people rush.

5. **Point to specific fields** in the JSON output — literally say "notice this
   field is null, not empty string." That detail is what impresses AI engineers.

6. **Don't apologize** for anything — no "this is just a prototype" or "I know
   it's not perfect." The eval scores are 30/30. Own it.

7. **The Arabic moment is your differentiator** — slow down and actually read
   the Arabic sentence in Segment 3. Even if your Arabic pronunciation is
   imperfect, the attempt shows you know what Gulf Arabic is.

---

## QUICK-RUN SHORTCUT

Save this as `demo/run_demo_curls.sh` and run it during recording:

```bash
#!/bin/bash
echo "=== CASE 1: Notify + Arabic (C-001) ==="
curl -s -X POST http://localhost:8000/notify-check \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "C-001"}' | python -m json.tool

echo ""
echo "=== CASE 2: Silence — Dead Zone (C-007) ==="
curl -s -X POST http://localhost:8000/notify-check \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "C-007"}' | python -m json.tool

echo ""
echo "=== CASE 3: Adversarial — All Products Owned (C-012) ==="
curl -s -X POST http://localhost:8000/notify-check \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "C-012"}' | python -m json.tool

echo ""
echo "=== CASE 4a: No DOB (C-018) ==="
curl -s -X POST http://localhost:8000/notify-check \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "C-018"}' | python -m json.tool

echo ""
echo "=== CASE 4b: Unknown Customer (C-FAKE) ==="
curl -s -X POST http://localhost:8000/notify-check \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "C-FAKE"}' | python -m json.tool
```

```bash
chmod +x demo/run_demo_curls.sh
```
