# CRITICAL: This module does NOT call any LLM.
# Age math must be deterministic and testable.
from datetime import date, timedelta
import json
from src.schemas import MilestoneCheck

class MilestoneCalculator:
    def __init__(self, rules_path: str):
        with open(rules_path) as f:
            self.rules = json.load(f)

    def calculate(self, child_dob: date | None, today: date = None) -> MilestoneCheck:
        if today is None:
            today = date.today()

        # Hard null path — no DOB means no calculation possible
        if child_dob is None:
            return MilestoneCheck(
                child_age_days=0, upcoming_milestone_id=None,
                upcoming_milestone_en=None, upcoming_milestone_ar=None,
                days_until_milestone=None, confidence=0.0
            )

        child_age_days = (today - child_dob).days

        # Pregnancy path — negative age means child not yet born
        # MS-025 fires when mother is in third trimester (due in ~60-90 days)
        if child_age_days < 0:
            days_until_birth = abs(child_age_days)
            if days_until_birth <= 90:  # third trimester window
                rule = next((r for r in self.rules if r['rule_id'] == 'MS-025'), None)
                if rule:
                    confidence = max(0.5, 1.0 - (abs(days_until_birth - 45) / 90))
                    return MilestoneCheck(
                        child_age_days=child_age_days,
                        upcoming_milestone_id=rule['rule_id'],
                        upcoming_milestone_en=rule['name_en'],
                        upcoming_milestone_ar=rule['name_ar'],
                        days_until_milestone=days_until_birth,
                        confidence=round(confidence, 2)
                    )
            return MilestoneCheck(
                child_age_days=child_age_days, upcoming_milestone_id=None,
                upcoming_milestone_en=None, upcoming_milestone_ar=None,
                days_until_milestone=None, confidence=0.0
            )

        # Child aged out of Mumzworld catalog (> 5 years = 1825 days)
        if child_age_days > 1825:
            return MilestoneCheck(
                child_age_days=child_age_days, upcoming_milestone_id=None,
                upcoming_milestone_en=None, upcoming_milestone_ar=None,
                days_until_milestone=None, confidence=0.0
            )

        # Find nearest upcoming milestone within 30-day window
        best = None
        best_days_away = 999

        for rule in self.rules:
            if rule['rule_id'] == 'MS-025':
                continue  # skip pregnancy milestone for born children
            target_day = rule['typical_age_days']
            days_away = target_day - child_age_days

            if 0 <= days_away <= 30:
                if days_away < best_days_away:
                    best_days_away = days_away
                    best = rule

        if best is None:
            return MilestoneCheck(
                child_age_days=child_age_days, upcoming_milestone_id=None,
                upcoming_milestone_en=None, upcoming_milestone_ar=None,
                days_until_milestone=None, confidence=0.0
            )

        # Confidence: peak at 7 days before, lower at 0 or 30 days
        days_to_peak = abs(best_days_away - 7)
        confidence = max(0.5, 1.0 - (days_to_peak / 30))

        return MilestoneCheck(
            child_age_days=child_age_days,
            upcoming_milestone_id=best['rule_id'],
            upcoming_milestone_en=best['name_en'],
            upcoming_milestone_ar=best['name_ar'],
            days_until_milestone=best_days_away,
            confidence=round(confidence, 2)
        )


if __name__ == "__main__":
    calc = MilestoneCalculator("data/milestone_rules.json")
    today = date.today()

    # Test 1: child 180 days old → Starting Solids
    dob_180 = today - __import__('datetime').timedelta(days=175)
    r = calc.calculate(dob_180)
    print(f"Test 1 (175d old): milestone={r.upcoming_milestone_en}, days_away={r.days_until_milestone}, conf={r.confidence}")
    assert r.upcoming_milestone_id == "MS-001", f"Expected MS-001, got {r.upcoming_milestone_id}"

    # Test 2: child 500 days old → no milestone
    dob_500 = today - __import__('datetime').timedelta(days=500)
    r2 = calc.calculate(dob_500)
    print(f"Test 2 (500d old): milestone={r2.upcoming_milestone_id}, conf={r2.confidence}")
    assert r2.upcoming_milestone_id is None

    # Test 3: no DOB
    r3 = calc.calculate(None)
    print(f"Test 3 (no DOB): milestone={r3.upcoming_milestone_id}, conf={r3.confidence}")
    assert r3.upcoming_milestone_id is None

    # Test 4: aged out (14 years)
    dob_old = today - __import__('datetime').timedelta(days=14*365)
    r4 = calc.calculate(dob_old)
    print(f"Test 4 (14yo): age={r4.child_age_days}d, milestone={r4.upcoming_milestone_id}")
    assert r4.upcoming_milestone_id is None

    # Test 5: confidence peak at 7 days before
    dob_7 = today - __import__('datetime').timedelta(days=173)  # MS-001 at 180, 7 days away
    r5 = calc.calculate(dob_7)
    print(f"Test 5 (7d to MS-001): conf={r5.confidence} (expect ~1.0)")
    assert r5.confidence >= 0.95

    print("All milestone_calculator tests passed ✓")
