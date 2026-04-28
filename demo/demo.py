#!/usr/bin/env python3
"""CLI demo: 5 Loom cases with rich terminal output."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv; load_dotenv()
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.text import Text
from src.pipeline import MomentEnginePipeline

console = Console()

CASES = [
    ("C-001", "Case 1 — Notify + Arabic (the money case)",
     "C-001: Fatima Al-Rashid | Language: AR | ~MS-001 Starting Solids"),
    ("C-007", "Case 2 — Silence is correct (dead zone)",
     "C-007: Jessica Williams | no milestone in next 30 days"),
    ("C-012", "Case 3 — Adversarial: all products already owned",
     "C-012: Noura Al-Rashidi | MS-001 real, but all feeding products owned"),
    ("C-018", "Case 4 — No DOB on file (new account)",
     "C-018: Sophie Anderson | no child_dob → explicit uncertainty"),
    ("C-FAKE", "Case 5 — Unknown customer ID",
     "C-FAKE-999: does not exist → graceful null, no 500"),
]

def render_bundle(bundle, customer_id: str):
    color = "green" if bundle.should_notify else "yellow"
    notify_text = Text(str(bundle.should_notify), style=f"bold {color}")

    # Header panel
    console.print(Panel(
        f"[bold]should_notify:[/bold] {notify_text}   "
        f"[bold]milestone_confidence:[/bold] {bundle.milestone_confidence:.2f}   "
        f"[bold]child_age_days:[/bold] {bundle.child_age_days}",
        border_style=color
    ))

    if bundle.should_notify:
        console.print(f"  [bold cyan]EN:[/bold cyan] {bundle.notification_copy_en}")
        console.print(f"  [bold green]AR:[/bold green] {bundle.notification_copy_ar}")
        console.print(f"  [bold]Milestone:[/bold] {bundle.moment_name_en} / {bundle.moment_name_ar}")

        if bundle.recommendations:
            t = Table(box=box.SIMPLE, show_header=True, header_style="bold magenta")
            t.add_column("Product ID", width=8)
            t.add_column("Name", width=30)
            t.add_column("Price (AED)", width=10)
            t.add_column("Age-Safe", width=8)
            t.add_column("Score", width=6)
            for r in bundle.recommendations:
                t.add_row(r.product_id, r.name_en, f"{r.price_aed:.0f}",
                          "✓" if r.age_safety_verified else "✗", f"{r.retrieval_score:.3f}")
            console.print(t)
        else:
            console.print("  [yellow]recommendations: [] (all products owned or out of stock)[/yellow]")
    else:
        console.print(f"  [yellow]notification_copy_en: null[/yellow]")
        console.print(f"  [yellow]notification_copy_ar: null[/yellow]")
        console.print(f"  [yellow]recommendations: []  ← not empty string, not None, just []  ✓[/yellow]")

    console.print(f"  [dim]reasoning: {bundle.reasoning[:100]}...[/dim]")
    console.print(f"  [dim]sources: {bundle.sources}[/dim]")
    console.print()

def main():
    console.print(Panel.fit(
        "[bold magenta]Mumzworld Moment Engine — Demo[/bold magenta]\n"
        "[dim]Life-stage aware notification personalizer | Track A | Satyam Ghosh[/dim]",
        border_style="magenta"
    ))
    console.print()

    pipeline = MomentEnginePipeline(
        "data/catalog.json", "data/customers.json", "data/milestone_rules.json"
    )

    for customer_id, title, subtitle in CASES:
        console.rule(f"[bold]{title}[/bold]")
        console.print(f"[dim]{subtitle}[/dim]")
        console.print()

        try:
            bundle = pipeline.run(customer_id)
            render_bundle(bundle, customer_id)
        except Exception as e:
            console.print(f"[red]ERROR: {e}[/red]")
            console.print()

    console.print(Panel.fit(
        "[bold green]Demo complete.[/bold green]\n"
        "[dim]Add OPENROUTER_API_KEY to .env for live LLM copy generation.[/dim]",
        border_style="green"
    ))

if __name__ == "__main__":
    main()
