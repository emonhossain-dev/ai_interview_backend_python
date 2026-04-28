# app/services/google_auth.py

from google.oauth2 import id_token
from google.auth.transport import requests
from app.core.config import GOOGLE_CLIENT_ID


def verify_google_token(token: str):
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        # extra safety checks
        if idinfo.get("iss") not in [
            "accounts.google.com",
            "https://accounts.google.com"
        ]:
            return None

        return {
            "email": idinfo.get("email"),
            "name": idinfo.get("name"),
            "picture": idinfo.get("picture")
        }

    except Exception:
        return None