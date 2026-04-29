#!/bin/bash
# Run all 5 demo curl cases against the running API server.
# Start server first with: python -m uvicorn api.main:app --port 8000

BASE="http://127.0.0.1:8000"

# Pretty-print JSON with Arabic rendered as readable text (not \uXXXX)
pretty() {
  python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin), ensure_ascii=False, indent=2))"
}

echo "=== CASE 1: Notify + Arabic (C-001 — Fatima, Starting Solids) ==="
curl -s -X POST $BASE/notify-check \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "C-001"}' | pretty

echo ""
echo "=== CASE 2: Silence — Dead Zone (C-007 — no milestone in 30 days) ==="
curl -s -X POST $BASE/notify-check \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "C-007"}' | pretty

echo ""
echo "=== CASE 3: Adversarial — All Products Owned (C-012) ==="
curl -s -X POST $BASE/notify-check \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "C-012"}' | pretty

echo ""
echo "=== CASE 4a: No DOB — New Account (C-018) ==="
curl -s -X POST $BASE/notify-check \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "C-018"}' | pretty

echo ""
echo "=== CASE 4b: Unknown Customer ID (C-FAKE) ==="
curl -s -X POST $BASE/notify-check \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "C-FAKE"}' | pretty
