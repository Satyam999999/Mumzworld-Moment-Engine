from pydantic import BaseModel, field_validator, model_validator
from typing import Literal

class MilestoneCheck(BaseModel):
    child_age_days: int
    upcoming_milestone_id: str | None
    upcoming_milestone_en: str | None
    upcoming_milestone_ar: str | None
    days_until_milestone: int | None
    confidence: float  # 0.0–1.0

    @field_validator('confidence')
    @classmethod
    def confidence_range(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('confidence must be between 0.0 and 1.0')
        return v

    @model_validator(mode='after')
    def milestone_fields_consistent(self):
        if self.upcoming_milestone_id:
            assert self.upcoming_milestone_en, \
                "milestone_en required when milestone_id is set"
            assert self.days_until_milestone is not None, \
                "days_until_milestone required when milestone_id is set"
        return self


class ProductRecommendation(BaseModel):
    product_id: str
    name_en: str
    name_ar: str
    price_aed: float
    age_safety_verified: bool       # True only if age range confirmed via RAG
    milestone_relevance: str        # one sentence: why this for this milestone
    retrieval_score: float          # cosine similarity from FAISS


class MomentBundle(BaseModel):
    should_notify: bool
    moment_name_en: str | None
    moment_name_ar: str | None
    notification_copy_en: str | None    # ≤ 25 words, warm, personal
    notification_copy_ar: str | None    # Gulf Arabic, not translated
    recommendations: list[ProductRecommendation]
    reasoning: str                      # always present
    sources: list[str]                  # product IDs + rule IDs
    child_age_days: int
    milestone_confidence: float

    @model_validator(mode='after')
    def notify_fields_consistent(self):
        if self.should_notify:
            assert self.notification_copy_en, \
                "EN copy required when should_notify is True"
            assert self.notification_copy_ar, \
                "AR copy required when should_notify is True — not optional"
            assert self.moment_name_en, \
                "moment_name_en required when should_notify is True"
        else:
            assert self.notification_copy_en is None, \
                "notification_copy_en must be null when should_notify is False"
            assert self.notification_copy_ar is None, \
                "notification_copy_ar must be null when should_notify is False"
            assert len(self.recommendations) == 0, \
                "recommendations must be empty when should_notify is False"
        return self


if __name__ == "__main__":
    # Validate MilestoneCheck
    mc = MilestoneCheck(
        child_age_days=175, upcoming_milestone_id="MS-001",
        upcoming_milestone_en="Starting Solids",
        upcoming_milestone_ar="بداية الأكل الصلب",
        days_until_milestone=5, confidence=0.9
    )
    print(f"MilestoneCheck OK: {mc.upcoming_milestone_en}, conf={mc.confidence}")

    # Validate null MilestoneCheck
    mc_null = MilestoneCheck(
        child_age_days=50, upcoming_milestone_id=None,
        upcoming_milestone_en=None, upcoming_milestone_ar=None,
        days_until_milestone=None, confidence=0.0
    )
    print(f"MilestoneCheck null OK: id={mc_null.upcoming_milestone_id}")

    # Validate ProductRecommendation
    pr = ProductRecommendation(
        product_id="MW-001", name_en="Chicco Weaning Set",
        name_ar="طقم الفطام", price_aed=89.0,
        age_safety_verified=True,
        milestone_relevance="BPA-free weaning kit for starting solids at 6 months.",
        retrieval_score=0.91
    )
    print(f"ProductRecommendation OK: {pr.product_id}")

    # Validate MomentBundle (notify=True)
    mb = MomentBundle(
        should_notify=True,
        moment_name_en="Starting Solids", moment_name_ar="بداية الأكل الصلب",
        notification_copy_en="Fatima, your baby is ready for first foods — here's what Mumzworld moms love.",
        notification_copy_ar="عزيزتي فاطمة، وقت الفطام اقترب لطفلتك الصغيرة 🌿",
        recommendations=[pr], reasoning="Milestone detected.", sources=["MW-001","MS-001"],
        child_age_days=175, milestone_confidence=0.9
    )
    print(f"MomentBundle notify=True OK: {mb.moment_name_en}")

    # Validate MomentBundle (notify=False)
    mb_null = MomentBundle(
        should_notify=False, moment_name_en=None, moment_name_ar=None,
        notification_copy_en=None, notification_copy_ar=None,
        recommendations=[], reasoning="No milestone imminent.",
        sources=[], child_age_days=50, milestone_confidence=0.0
    )
    print(f"MomentBundle notify=False OK: copies={mb_null.notification_copy_en}")
    print("All schema validations passed ✓")
