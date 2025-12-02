import re
from .gmail import list_latest_emails, send_email, delete_email_by_id
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import List, Literal, Optional

from .utils import decode_access_token
from .gmail import list_latest_emails, send_email, delete_email_by_id
from .ai import summarize_email, generate_reply, daily_digest

router = APIRouter()

class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class ChatCommandRequest(BaseModel):
    message: str
    context: Optional[List[ChatMessage]] = None

class ChatResponse(BaseModel):
    messages: List[ChatMessage]

def _get_session_payload(request: Request):
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload

# def _simple_intent_detection(text: str) -> str:
#     t = text.lower()
#     if "last" in t and "email" in t:
#         return "list"
#     if "delete" in t:
#         return "delete"
#     if "reply" in t:
#         return "reply"
#     if "digest" in t:
#         return "digest"
#     return "smalltalk"
def _simple_intent_detection(text: str) -> str:
    t = text.lower()

    if "delete" in t:
        return "delete"
    if "digest" in t:
        return "digest"
    if "reply" in t:
        return "reply"
    if "last" in t and "email" in t:
        return "list"
    return "smalltalk"

def _parse_delete_command(text: str):
    t = text.lower()

    # "delete email 3"
    match = re.search(r"delete\s+(?:email|mail)\s+(\d+)", t)
    if match:
        return {"mode": "index", "index": int(match.group(1))}

    # "delete last email" / "delete latest email"
    if "delete last email" in t or "delete latest email" in t:
        return {"mode": "last"}

    return None



@router.post("/command", response_model=ChatResponse)
async def handle_command(payload: ChatCommandRequest, request: Request):
    session = _get_session_payload(request)
    user = session["user"]
    google_tokens = session["google"]

    user_msg = ChatMessage(role="user", content=payload.message)
    assistant_msgs: list[ChatMessage] = []

    intent = _simple_intent_detection(payload.message)

    if intent == "list":
        assistant_msgs.append(ChatMessage(role="assistant", content="Fetching your latest emails..."))
        emails = list_latest_emails(google_tokens, max_results=5)
        lines = []
        for i, e in enumerate(emails, start=1):
            summary = await summarize_email(e["body"])
            lines.append(f"{i}. From: {e['sender']}\n   Subject: {e['subject']}\n   Summary: {summary}")
        assistant_msgs.append(ChatMessage(role="assistant", content="\n\n".join(lines)))

    elif intent == "delete":
        parsed = _parse_delete_command(user_msg.content)

        if not parsed:
            # ❗ parsed is None → we DON'T touch parsed["..."] here
                assistant_msgs.append(
                    ChatMessage(
                    role="assistant",
                    content="Please tell me which email to delete, e.g. 'delete email 2' or 'delete last email'.",
                )
            )
        else:
            assistant_msgs.append(
                ChatMessage(
                    role="assistant",
                    content="Okay, checking your recent emails to delete the right one...",
                )
            )

            emails = list_latest_emails(google_tokens, max_results=5)

            if not emails:
                assistant_msgs.append(
                    ChatMessage(
                        role="assistant",
                        content="I couldn't find any recent emails to delete.",
                    )
                )
            else:
                if parsed["mode"] == "last":
                    idx = len(emails) - 1
                else:
                    idx = parsed["index"] - 1

                if idx < 0 or idx >= len(emails):
                    assistant_msgs.append(
                        ChatMessage(
                            role="assistant",
                            content=f"I only fetched {len(emails)} recent emails, so I can't delete email {parsed.get('index')}.",
                        )
                    )
                else:
                    target = emails[idx]
                    delete_email_by_id(google_tokens, target["id"])
                    assistant_msgs.append(
                        ChatMessage(
                            role="assistant",
                            content=(
                                f"Deleted email {idx + 1}:\n"
                                f"From: {target['sender']}\n"
                                f"Subject: {target['subject']}"
                            ),
                        )
                    )

    elif intent == "reply":
        assistant_msgs.append(ChatMessage(role="assistant", content="Reply feature placeholder – will generate replies based on recent email."))
    elif intent == "digest":
        assistant_msgs.append(ChatMessage(role="assistant", content="Generating today's email digest..."))
        emails = list_latest_emails(google_tokens, max_results=20)
        digest = await daily_digest(emails)
        assistant_msgs.append(ChatMessage(role="assistant", content=digest))
    else:
        assistant_msgs.append(ChatMessage(role="assistant", content="I can help you with your emails. Try: 'show my last 5 emails' or 'give me today's email digest'."))

    return ChatResponse(messages=[user_msg] + assistant_msgs)
