from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from tenacity import retry, stop_after_attempt, wait_exponential
import base64
import email
from email.message import EmailMessage
import logging
from .config import settings

logger = logging.getLogger("constructure-ai")
logging.basicConfig(level=logging.INFO)

ALGORITHM = "HS256"

def create_access_token(data: dict, expires_minutes: int | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=expires_minutes or settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.session_secret_key, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.session_secret_key, algorithms=[ALGORITHM])
    except JWTError:
        return None

def retryable(fn):
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )(fn)

def parse_gmail_message(msg: dict) -> dict:
    """Extract sender, subject, plain text body from Gmail API message."""
    headers = msg.get("payload", {}).get("headers", [])
    header_map = {h["name"].lower(): h["value"] for h in headers}
    subject = header_map.get("subject", "")
    sender = header_map.get("from", "")

    body = ""
    payload = msg.get("payload", {})
    parts = payload.get("parts", [])
    data = None

    if parts:
        for p in parts:
            if p.get("mimeType") == "text/plain":
                data = p.get("body", {}).get("data")
                break
    else:
        data = payload.get("body", {}).get("data")

    if data:
        body_bytes = base64.urlsafe_b64decode(data.encode("utf-8"))
        body = body_bytes.decode("utf-8", errors="ignore")

    return {
        "id": msg.get("id"),
        "threadId": msg.get("threadId"),
        "subject": subject,
        "sender": sender,
        "body": body,
    }

def build_raw_email(to_email: str, subject: str, body: str, from_email: str) -> str:
    message = EmailMessage()
    message["To"] = to_email
    message["From"] = from_email
    message["Subject"] = subject
    message.set_content(body)
    raw_bytes = base64.urlsafe_b64encode(message.as_bytes())
    return raw_bytes.decode("utf-8")
