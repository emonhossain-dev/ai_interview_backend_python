from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from uuid import UUID
from fastapi import HTTPException

from app.models.subscription import (
    Plan, Subscription, Payment, UsageLog,
    BillingCycle, SubscriptionStatus, PaymentStatus
)
from app.models.user import User


# ─────────────────────────────────────────────
# PLAN  helpers
# ─────────────────────────────────────────────

def get_all_plans(db: Session):
    return db.query(Plan).all()


def get_plan_by_id(db: Session, plan_id: UUID):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


# ─────────────────────────────────────────────
# SUBSCRIPTION  helpers
# ─────────────────────────────────────────────

def get_active_subscription(db: Session, user_id: int):
    """User এর current active subscription ফেরত দেয়। না থাকলে None."""
    return (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user_id,
            Subscription.status  == SubscriptionStatus.active
        )
        .first()
    )


def create_subscription(db: Session, user_id: int, plan_id: UUID, billing_cycle: BillingCycle):
    """
    নতুন subscription তৈরি করে।
    আগের active subscription থাকলে cancel করে নেয়।
    """
    plan = get_plan_by_id(db, plan_id)

    # পুরনো active sub cancel করো
    old_sub = get_active_subscription(db, user_id)
    if old_sub:
        old_sub.status       = SubscriptionStatus.cancelled
        old_sub.cancelled_at = datetime.now(timezone.utc)

    now = datetime.now(timezone.utc)
    if billing_cycle == BillingCycle.yearly:
        period_end = now + timedelta(days=365)
        amount     = float(plan.yearly_price)
    else:
        period_end = now + timedelta(days=30)
        amount     = float(plan.monthly_price)

    sub = Subscription(
        user_id              = user_id,
        plan_id              = plan_id,
        billing_cycle        = billing_cycle,
        status               = SubscriptionStatus.active,
        current_period_start = now,
        current_period_end   = period_end,
    )
    db.add(sub)
    db.flush()   # sub.id দরকার payment এর জন্য

    # Payment record তৈরি করো (pending)
    payment = Payment(
        subscription_id = sub.id,
        user_id         = user_id,
        amount          = amount,
        currency        = "BDT",
        status          = PaymentStatus.pending,
    )
    db.add(payment)
    db.commit()
    db.refresh(sub)

    return sub, payment


def cancel_subscription(db: Session, user_id: int):
    sub = get_active_subscription(db, user_id)
    if not sub:
        raise HTTPException(status_code=404, detail="No active subscription found")

    sub.status       = SubscriptionStatus.cancelled
    sub.cancelled_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(sub)
    return sub


# ─────────────────────────────────────────────
# PAYMENT  helpers
# ─────────────────────────────────────────────

def confirm_payment(db: Session, subscription_id: UUID, gateway: str, gateway_txn_id: str):
    """
    Gateway callback এ payment confirm করো।
    Real project এ এখানে gateway signature verify করতে হবে।
    """
    payment = (
        db.query(Payment)
        .filter(
            Payment.subscription_id == subscription_id,
            Payment.status          == PaymentStatus.pending
        )
        .order_by(Payment.created_at.desc())
        .first()
    )

    if not payment:
        raise HTTPException(status_code=404, detail="Pending payment not found")

    payment.status         = PaymentStatus.success
    payment.gateway        = gateway
    payment.gateway_txn_id = gateway_txn_id
    payment.paid_at        = datetime.now(timezone.utc)

    db.commit()
    db.refresh(payment)
    return payment


def get_payment_history(db: Session, user_id: int):
    return (
        db.query(Payment)
        .filter(Payment.user_id == user_id)
        .order_by(Payment.created_at.desc())
        .all()
    )


# ─────────────────────────────────────────────
# USAGE  helpers
# ─────────────────────────────────────────────

def get_today_usage(db: Session, user_id: int):
    """আজকের usage log ফেরত দেয়। না থাকলে নতুন বানায়।"""
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    log = (
        db.query(UsageLog)
        .filter(
            UsageLog.user_id  == user_id,
            UsageLog.log_date >= today_start
        )
        .first()
    )

    if not log:
        log = UsageLog(
            user_id  = user_id,
            log_date = today_start,
            interviews_used    = 0,
            voice_minutes_used = 0,
        )
        db.add(log)
        db.commit()
        db.refresh(log)

    return log


def can_start_interview(db: Session, user_id: int) -> bool:
    """Free plan daily limit check। Pro হলে সবসময় True।"""
    sub  = get_active_subscription(db, user_id)
    plan = sub.plan if sub else None

    # subscription নেই বা free plan
    if not plan or plan.interview_limit is None:
        # interview_limit = NULL মানে unlimited (pro)
        if plan and plan.interview_limit is None:
            return True

    limit = plan.interview_limit if plan else 3   # default free limit = 3

    log = get_today_usage(db, user_id)
    return log.interviews_used < limit


def increment_interview_usage(db: Session, user_id: int):
    log = get_today_usage(db, user_id)
    log.interviews_used += 1
    db.commit()


def increment_voice_usage(db: Session, user_id: int, minutes: int):
    log = get_today_usage(db, user_id)
    log.voice_minutes_used += minutes
    db.commit()


def get_user_usage_summary(db: Session, user_id: int):
    """Dashboard এ দেখানোর জন্য usage summary।"""
    sub  = get_active_subscription(db, user_id)
    plan = sub.plan if sub else None
    log  = get_today_usage(db, user_id)

    return {
        "interviews_used":    log.interviews_used,
        "interview_limit":    plan.interview_limit if plan else 3,
        "voice_minutes_used": log.voice_minutes_used,
        "has_voice_ai":       plan.has_voice_ai if plan else False,
        "show_ads":           plan.show_ads if plan else True,
        "plan_name":          plan.name if plan else "Free",
        "plan_type":          plan.type.value if plan else "free",
    }
