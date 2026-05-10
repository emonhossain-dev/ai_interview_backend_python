from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.subscription import BillingCycle
from app.utils.current_user_token_check import get_current_user
from app.schemas.subscription import (
    SubscriptionCreate, SubscriptionResponse,
    PaymentCallbackRequest, PaymentResponse,
    PlanResponse, UsageResponse
)
from app.services.subscription_service import (
    get_all_plans,
    get_plan_by_id,
    get_active_subscription,
    create_subscription,
    cancel_subscription,
    confirm_payment,
    get_payment_history,
    get_user_usage_summary,
)

router = APIRouter()


# ─────────────────────────────────────────────
# PLANS
# ─────────────────────────────────────────────

@router.get("/plans", response_model=list[PlanResponse])
def list_plans(db: Session = Depends(get_db)):
    """সব available plan দেখাও — auth লাগবে না।"""
    return get_all_plans(db)


@router.get("/plans/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: UUID, db: Session = Depends(get_db)):
    return get_plan_by_id(db, plan_id)


# ─────────────────────────────────────────────
# MY SUBSCRIPTION
# ─────────────────────────────────────────────

@router.get("/my", response_model=SubscriptionResponse | None)
def my_subscription(
    user: User    = Depends(get_current_user),
    db:   Session = Depends(get_db)
):
    """Login করা user এর active subscription।"""
    sub = get_active_subscription(db, user.id)
    return sub   # None হলে 200 + null — frontend handle করবে


@router.post("/subscribe", response_model=SubscriptionResponse)
def subscribe(
    data: SubscriptionCreate,
    user: User    = Depends(get_current_user),
    db:   Session = Depends(get_db)
):
    """
    নতুন plan subscribe করো।
    Response এ subscription + pending payment আসবে।
    Payment confirm হলে /payment/confirm call করো।
    """
    sub, payment = create_subscription(
        db            = db,
        user_id       = user.id,
        plan_id       = data.plan_id,
        billing_cycle = data.billing_cycle,
    )
    return sub


@router.post("/cancel")
def cancel(
    user: User    = Depends(get_current_user),
    db:   Session = Depends(get_db)
):
    sub = cancel_subscription(db, user.id)
    return {
        "message":      "Subscription cancelled",
        "cancelled_at": sub.cancelled_at
    }


# ─────────────────────────────────────────────
# PAYMENT
# ─────────────────────────────────────────────

@router.post("/payment/confirm", response_model=PaymentResponse)
def payment_confirm(
    data: PaymentCallbackRequest,
    user: User    = Depends(get_current_user),
    db:   Session = Depends(get_db)
):
    """
    Gateway payment সফল হলে এই endpoint call করো।
    gateway_txn_id = gateway দেওয়া transaction id।
    """
    payment = confirm_payment(
        db              = db,
        subscription_id = data.subscription_id,
        gateway         = data.gateway,
        gateway_txn_id  = data.gateway_txn_id,
    )
    return payment


@router.get("/payment/history", response_model=list[PaymentResponse])
def payment_history(
    user: User    = Depends(get_current_user),
    db:   Session = Depends(get_db)
):
    return get_payment_history(db, user.id)


# ─────────────────────────────────────────────
# USAGE
# ─────────────────────────────────────────────

@router.get("/usage", response_model=UsageResponse)
def usage_summary(
    user: User    = Depends(get_current_user),
    db:   Session = Depends(get_db)
):

    return get_user_usage_summary(db, user.id)
