#!/usr/bin/env python3
"""Run all 15 eval cases and write results to eval/evaluation_results.csv"""
import sys, os, json, csv
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv; load_dotenv()
from src.pipeline import MomentEnginePipeline

def run():
    pipeline = MomentEnginePipeline(
        "data/catalog.json", "data/customers.json", "data/milestone_rules.json"
    )
    with open("eval/test_cases.json") as f:
        cases = json.load(f)

    rows = []
    for tc in cases:
        cid = tc["customer_id"]
        print(f"  Running case {tc['case_id']}: {cid}...", end="\r", flush=True)

        try:
            b = pipeline.run(cid)
            got_notify   = b.should_notify
            milestone    = b.moment_name_en or "—"
            en_copy      = b.notification_copy_en or "null"
            ar_copy      = b.notification_copy_ar or "null"
            recs         = ", ".join(r.product_id for r in b.recommendations) or "[]"
            confidence   = f"{b.milestone_confidence:.2f}"
            reasoning    = b.reasoning[:120].replace("\n", " ")
            crash        = ""
        except Exception as e:
            got_notify = None
            milestone = ar_copy = en_copy = recs = confidence = reasoning = "—"
            crash = str(e)[:80]

        exp = tc["expected_notify"]

        # Determine pass/fail
        if crash:
            verdict = "FAIL"
        elif got_notify != exp:
            verdict = "FAIL"
        elif exp is False:
            # Silent path: check null hygiene
            if b.notification_copy_en is not None or b.notification_copy_ar is not None or b.recommendations:
                verdict = "FAIL"
            else:
                verdict = "PASS"
        else:
            # Notify=True path: check EN + AR present
            if b.notification_copy_en and b.notification_copy_ar:
                verdict = "PASS"
            else:
                verdict = "PARTIAL"

        # Build expected output description
        if exp:
            exp_out = f"should_notify=True | EN copy ≤25w | AR copy (Gulf) | milestone in window"
        else:
            exp_out = f"should_notify=False | notification_copy_en=null | notification_copy_ar=null | recommendations=[]"

        # Build actual output description
        if crash:
            act_out = f"CRASH: {crash}"
        elif exp:
            act_out = (f"should_notify={got_notify} | milestone={milestone} | "
                       f"conf={confidence} | recs=[{recs}] | "
                       f"EN='{en_copy[:60]}' | AR='{ar_copy[:60]}'")
        else:
            act_out = (f"should_notify={got_notify} | EN={en_copy} | AR={ar_copy} | "
                       f"recs=[{recs}] | reasoning='{reasoning[:80]}'")

        rows.append({
            "case_id"        : tc["case_id"],
            "group"          : tc["group"],
            "description"    : tc["description"],
            "customer_id"    : cid,
            "expected_notify": exp,
            "actual_notify"  : got_notify,
            "verdict"        : verdict,
            "milestone"      : milestone,
            "confidence"     : confidence,
            "expected_output": exp_out,
            "actual_output"  : act_out,
            "notes"          : tc.get("notes", ""),
        })

    # Write CSV
    out_path = "eval/evaluation_results.csv"
    fieldnames = [
        "case_id","group","description","customer_id",
        "expected_notify","actual_notify","verdict",
        "milestone","confidence","expected_output","actual_output","notes"
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Summary
    passed  = sum(1 for r in rows if r["verdict"] == "PASS")
    partial = sum(1 for r in rows if r["verdict"] == "PARTIAL")
    failed  = sum(1 for r in rows if r["verdict"] == "FAIL")
    points  = passed * 2 + partial * 1

    print(f"\n{'='*60}")
    print(f"CSV written to: {out_path}")
    print(f"PASS: {passed} | PARTIAL: {partial} | FAIL: {failed}")
    print(f"Score: {points}/30 points ({passed}/15 PASS)")
    print(f"{'='*60}")

if __name__ == "__main__":
    run()
