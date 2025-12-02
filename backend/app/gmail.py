from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from fastapi import HTTPException
from .utils import retryable, parse_gmail_message, build_raw_email

def _build_service(google_tokens: dict):
    creds = Credentials(
        token=google_tokens["access_token"],
        refresh_token=google_tokens.get("refresh_token"),
        token_uri=google_tokens["token_uri"],
        client_id=google_tokens["client_id"],
        client_secret=google_tokens["client_secret"],
        scopes=google_tokens.get("scopes", []),
    )
    return build("gmail", "v1", credentials=creds)

@retryable
def list_latest_emails(google_tokens: dict, max_results: int = 5):
    service = _build_service(google_tokens)
    resp = service.users().messages().list(userId="me", maxResults=max_results).execute()
    ids = resp.get("messages", [])
    messages = []
    for m in ids:
        msg = service.users().messages().get(userId="me", id=m["id"], format="full").execute()
        messages.append(parse_gmail_message(msg))
    return messages

@retryable
def send_email(google_tokens: dict, from_email: str, to_email: str, subject: str, body: str):
    service = _build_service(google_tokens)
    raw = build_raw_email(to_email, subject, body, from_email)
    message = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    return message

@retryable
def delete_email_by_id(google_tokens: dict, msg_id: str):
    service = _build_service(google_tokens)
    service.users().messages().delete(userId="me", id=msg_id).execute()
    return True
