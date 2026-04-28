import secrets

from datetime import datetime, timedelta, timezone


# -------------------------
# OTP GENERATOR (SECURE)
# -------------------------
def generate_otp() -> str:
    return str(secrets.randbelow(900000) + 100000)  # 6-digit secure OTP


# -------------------------
# OTP EXPIRY (UTC SAFE)

def get_otp_expiry():
    return datetime.now(timezone.utc) + timedelta(minutes=10)