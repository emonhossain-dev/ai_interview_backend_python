from sqlalchemy import (
    Column, String, Boolean, DateTime, ForeignKey,
    Numeric, Integer, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
import enum

from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


# ─────────────────────────────────────────────
# ENUMS
# ─────────────────────────────────────────────

class PlanType(str, enum.Enum):
    free  = "free"
    pro   = "pro"

class BillingCycle(str, enum.Enum):
    monthly = "monthly"
    yearly  = "yearly"

class SubscriptionStatus(str, enum.Enum):
    active    = "active"
    cancelled = "cancelled"
    expired   = "expired"
    trialing  = "trialing"

class PaymentStatus(str, enum.Enum):
    pending   = "pending"
    success   = "success"
    failed    = "failed"
    refunded  = "refunded"


# ─────────────────────────────────────────────
# PLAN  (Free / Pro Monthly / Pro Yearly)
# ─────────────────────────────────────────────

class Plan(Base):
    __tablename__ = "plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name         = Column(String, nullable=False, unique=True)   # "Free", "Pro"
    type         = Column(SAEnum(PlanType), nullable=False)       # free | pro

    monthly_price = Column(Numeric(10, 2), default=0.00)
    yearly_price  = Column(Numeric(10, 2), default=0.00)

    # ── Feature flags ──
    interview_limit       = Column(Integer, nullable=True)   # NULL = unlimited
    has_voice_ai          = Column(Boolean, default=False)
    has_advanced_report   = Column(Boolean, default=False)
    show_ads              = Column(Boolean, default=True)
    ai_model_tier         = Column(String, default="basic")  # "basic" | "premium"

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    subscriptions = relationship("Subscription", back_populates="plan")


# ─────────────────────────────────────────────
# SUBSCRIPTION
# ─────────────────────────────────────────────

class Subscription(Base):
    __tablename__ = "subscriptions"

    id      = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=False)

    billing_cycle = Column(SAEnum(BillingCycle), nullable=False, default=BillingCycle.monthly)
    status        = Column(SAEnum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.active)

    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end   = Column(DateTime(timezone=True), nullable=False)
    cancelled_at         = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # ── Relations ──
    user     = relationship("User", back_populates="subscriptions")
    plan     = relationship("Plan", back_populates="subscriptions")
    payments = relationship("Payment", back_populates="subscription", cascade="all, delete-orphan")


# ─────────────────────────────────────────────
# PAYMENT
# ─────────────────────────────────────────────

class Payment(Base):
    __tablename__ = "payments"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=False, index=True)
    user_id         = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    amount   = Column(Numeric(10, 2), nullable=False)
    currency = Column(String, default="BDT")
    status   = Column(SAEnum(PaymentStatus), nullable=False, default=PaymentStatus.pending)

    gateway        = Column(String, nullable=True)   # "sslcommerz" | "bkash" | "stripe"
    gateway_txn_id = Column(String, nullable=True)   # gateway দেওয়া transaction id
    invoice_url    = Column(String, nullable=True)

    paid_at    = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # ── Relations ──
    subscription = relationship("Subscription", back_populates="payments")
    user         = relationship("User", back_populates="payments")


# ─────────────────────────────────────────────
# USAGE LOG  (daily interview + voice tracking)
# ─────────────────────────────────────────────

class UsageLog(Base):
    __tablename__ = "usage_logs"

    id      = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    log_date            = Column(DateTime(timezone=True), nullable=False)  # date of usage
    interviews_used     = Column(Integer, default=0)
    voice_minutes_used  = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="usage_logs")
