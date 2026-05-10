from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.subscription import BillingCycle, PaymentStatus


# ─────────────────────────────────────────────
# PLAN
# ─────────────────────────────────────────────

class PlanResponse(BaseModel):
    id:                   UUID
    name:                 str
    type:                 str
    monthly_price:        float
    yearly_price:         float
    interview_limit:      Optional[int]
    has_voice_ai:         bool
    has_advanced_report:  bool
    show_ads:             bool
    ai_model_tier:        str

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# SUBSCRIPTION
# ─────────────────────────────────────────────

class SubscriptionCreate(BaseModel):
    plan_id:       UUID
    billing_cycle: BillingCycle   # "monthly" | "yearly"


class SubscriptionResponse(BaseModel):
    id:                   UUID
    plan_id:              UUID
    billing_cycle:        str
    status:               str
    current_period_start: datetime
    current_period_end:   datetime
    cancelled_at:         Optional[datetime]
    created_at:           datetime

    plan: PlanResponse

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# PAYMENT
# ─────────────────────────────────────────────

class PaymentInitRequest(BaseModel):
    subscription_id: UUID
    gateway:         str   # "sslcommerz" | "bkash" | "stripe"

class PaymentCallbackRequest(BaseModel):
    gateway_txn_id:  str
    subscription_id: UUID
    status:          PaymentStatus

class PaymentResponse(BaseModel):
    id:              UUID
    amount:          float
    currency:        str
    status:          str
    gateway:         str
    gateway_txn_id:  Optional[str]
    paid_at:         Optional[datetime]
    created_at:      datetime

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# USAGE
# ─────────────────────────────────────────────

class UsageResponse(BaseModel):
    interviews_used:    int
    interview_limit:    Optional[int]   # None = unlimited
    voice_minutes_used: int
    has_voice_ai:       bool
    show_ads:           bool
    plan_name:          str
    plan_type:          str
