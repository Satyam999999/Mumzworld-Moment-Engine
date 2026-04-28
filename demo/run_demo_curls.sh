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
echo "=== CASE 4a: No DOB — New Account (C-018) ==="
curl -s -X POST http://localhost:8000/notify-check \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "C-018"}' | python -m json.tool

echo ""
echo "=== CASE 4b: Unknown Customer (C-FAKE) ==="
curl -s -X POST http://localhost:8000/notify-check \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "C-FAKE"}' | python -m json.tool
