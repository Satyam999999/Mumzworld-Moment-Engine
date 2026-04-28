from datetime import date
from src.schemas import MomentBundle
from src.milestone_calculator import MilestoneCalculator
from src.retriever import ProductRetriever
from src.deduplicator import deduplicate
from src.agent import build_agent, AgentState
import json

class MomentEnginePipeline:
    def __init__(self, catalog_path: str, customers_path: str, rules_path: str):
        self.calculator = MilestoneCalculator(rules_path)
        self.retriever = ProductRetriever(catalog_path)
        self.agent = build_agent()
        with open(customers_path) as f:
            self.customers = {c['customer_id']: c for c in json.load(f)}
        with open(catalog_path) as f:
            self.catalog = {p['product_id']: p for p in json.load(f)}

    def run(self, customer_id: str) -> MomentBundle:
        customer = self.customers.get(customer_id)
        if not customer:
            return MomentBundle(
                should_notify=False, moment_name_en=None, moment_name_ar=None,
                notification_copy_en=None, notification_copy_ar=None,
                recommendations=[], reasoning=f"Customer {customer_id} not found.",
                sources=[], child_age_days=0, milestone_confidence=0.0
            )

        dob = None
        if customer.get('child_dob'):
            dob = date.fromisoformat(customer['child_dob'])

        milestone = self.calculator.calculate(dob)

        candidates = []
        if milestone.confidence >= 0.75 and milestone.upcoming_milestone_id:
            child_age_months = milestone.child_age_days // 30
            query = f"{milestone.upcoming_milestone_en} products for baby child"
            raw_candidates = self.retriever.search(
                query=query,
                child_age_months=child_age_months,
                exclude_product_ids=customer.get('purchase_history', [])
            )
            owned_products = [
                self.catalog[pid]
                for pid in customer.get('purchase_history', [])
                if pid in self.catalog
            ]
            candidates = deduplicate(raw_candidates, customer.get('purchase_history', []), owned_products)

        initial_state = AgentState(
            customer=customer, milestone=milestone,
            candidates=candidates, bundle=None, error=None,
            _en_raw='', _ar_raw=''
        )
        final_state = self.agent.invoke(initial_state)
        return final_state['bundle']


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    pipeline = MomentEnginePipeline(
        catalog_path="data/catalog.json",
        customers_path="data/customers.json",
        rules_path="data/milestone_rules.json"
    )
    print("Running pipeline for C-001 (Fatima, AR, ~MS-001)...\n")
    bundle = pipeline.run("C-001")
    print(bundle.model_dump_json(indent=2))
