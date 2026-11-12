#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json

def parse_amount(val):
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        cleaned = val.replace(",", "").strip()
        return float(cleaned)
    return float(val)

# Map each txn_id to its latest attempt event
latest_attempts = {}

with open("payments.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except Exception:
            # Ignore lines that can't be read
            continue

        # Ignore events without a txn_id
        if not isinstance(event, dict) or not event.get("txn_id"):
            continue

        txn_id = event["txn_id"]
        ts = event.get("ts", "")

        # Only the latest attempt for each txn_id counts
        if txn_id not in latest_attempts or ts > latest_attempts[txn_id].get("ts", ""):
            latest_attempts[txn_id] = event

count = 0
total = 0.0

for event in latest_attempts.values():
    # A payment counts as collected only if its latest attempt is success
    if event.get("status") == "success":
        count += 1
        total += parse_amount(event.get("amount", 0))

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
