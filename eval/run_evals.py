#!/usr/bin/env python3
"""Run all 15 eval cases and print a rich score table."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv; load_dotenv()
from rich.table import Table
from rich.console import Console
from rich import box
from src.pipeline import MomentEnginePipeline

console = Console()

def score_case(tc: dict, bundle) -> tuple[str, int, str]:
    """Return (result_label, points, notes)."""
    expected = tc['expected_notify']
    got = bundle.should_notify

    # Basic correctness
    if got != expected:
        return "FAIL", 0, f"Expected notify={expected}, got {got}"

    notes_parts = []

    # Null-field hygiene (critical)
    if not expected:
        if bundle.notification_copy_en is not None:
            return "FAIL", 0, "EN copy not null when should_notify=False"
        if bundle.notification_copy_ar is not None:
            return "FAIL", 0, "AR copy not null when should_notify=False"
        if bundle.recommendations:
            return "FAIL", 0, "recommendations not empty when should_notify=False"
        return "PASS", 2, "Silent correctly — null fields ✓"

    # Notify=True checks
    if expected:
        if not bundle.notification_copy_en:
            return "FAIL", 0, "EN copy missing"
        if not bundle.notification_copy_ar:
            return "PARTIAL", 1, "AR copy missing — partial"
        if tc.get('expected_milestone_contains'):
            kw = tc['expected_milestone_contains']
            if kw.lower() not in (bundle.moment_name_en or '').lower():
                notes_parts.append(f"Milestone name mismatch (expected '{kw}')")
        if notes_parts:
            return "PARTIAL", 1, "; ".join(notes_parts)
        return "PASS", 2, f"notify ✓ | AR ✓ | {len(bundle.recommendations)} rec(s)"

    return "PASS", 2, ""

def main():
    pipeline = MomentEnginePipeline(
        "data/catalog.json", "data/customers.json", "data/milestone_rules.json"
    )
    with open("eval/test_cases.json") as f:
        cases = json.load(f)

    table = Table(title="Mumzworld Moment Engine — Eval Results",
                  box=box.ROUNDED, show_lines=True)
    table.add_column("Case", style="cyan", width=4)
    table.add_column("Group", width=12)
    table.add_column("Description", width=40)
    table.add_column("Exp.", width=5)
    table.add_column("Got", width=5)
    table.add_column("Result", width=8)
    table.add_column("Score", width=5)
    table.add_column("Notes", width=35)

    total_points = 0
    passed = 0

    for tc in cases:
        cid = tc['customer_id']
        console.print(f"  Running case {tc['case_id']}: {cid}...", end="\r")
        try:
            bundle = pipeline.run(cid)
            label, pts, notes = score_case(tc, bundle)
        except Exception as e:
            label, pts, notes = "FAIL", 0, f"CRASH: {str(e)[:40]}"
            bundle = None

        total_points += pts
        if label == "PASS": passed += 1

        got_str = str(bundle.should_notify) if bundle else "ERR"
        color = "green" if label == "PASS" else ("yellow" if label == "PARTIAL" else "red")

        table.add_row(
            str(tc['case_id']), tc['group'],
            tc['description'][:38],
            str(tc['expected_notify']), got_str,
            f"[{color}]{label}[/{color}]", f"{pts}/2", notes[:33]
        )

    console.print()
    console.print(table)
    console.print()
    console.print(f"[bold]Score: {total_points}/30 points ({passed}/15 cases PASS)[/bold]")
    console.print(f"[dim]Note: Cases requiring OpenRouter API will PARTIAL if key not set.[/dim]")

if __name__ == "__main__":
    main()
