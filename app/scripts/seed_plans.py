"""
python -m app.scripts.seed_plans

এই script run করলে database এ Free ও Pro plan তৈরি হবে।
একবারই run করতে হবে।
"""

from app.database import SessionLocal
from app.models.subscription import Plan, PlanType


def seed_plans():
    db = SessionLocal()

    try:
        existing = db.query(Plan).count()
        if existing > 0:
            print("✅ Plans already seeded. Skipping.")
            return

        plans = [
            Plan(
                name                = "Free",
                type                = PlanType.free,
                monthly_price       = 0.00,
                yearly_price        = 0.00,
                interview_limit     = 3,        # দিনে ৩টা
                has_voice_ai        = False,
                has_advanced_report = False,
                show_ads            = True,
                ai_model_tier       = "basic",
            ),
            Plan(
                name                = "Pro",
                type                = PlanType.pro,
                monthly_price       = 299.00,   # BDT — নিজের মতো বদলাও
                yearly_price        = 2499.00,
                interview_limit     = None,     # NULL = unlimited
                has_voice_ai        = True,
                has_advanced_report = True,
                show_ads            = False,
                ai_model_tier       = "premium",
            ),
        ]

        db.add_all(plans)
        db.commit()
        print("✅ Plans seeded successfully!")
        for p in plans:
            db.refresh(p)
            print(f"   → {p.name}  (id: {p.id})")

    finally:
        db.close()


if __name__ == "__main__":
    seed_plans()
