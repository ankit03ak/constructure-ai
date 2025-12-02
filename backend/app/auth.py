from fastapi import APIRouter, Request, Response, HTTPException, status
from pydantic import BaseModel
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from google.auth import exceptions as google_exceptions  # 👈 NEW

from .config import settings
from .utils import create_access_token, decode_access_token

router = APIRouter()


class User(BaseModel):
    id: str
    email: str
    name: str | None = None
    picture: str | None = None


class MeResponse(BaseModel):
    user: User


def _get_flow() -> Flow:
    return Flow.from_client_config(
        {
            "web": {
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.google_redirect_uri],
            }
        },
        scopes=settings.google_oauth_scopes.split(),
    )


@router.get("/google/login")
def google_login():
    flow = _get_flow()
    flow.redirect_uri = settings.google_redirect_uri
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    # For simplicity, we don't persist state here; you can skip CSRF for the challenge.
    return {"auth_url": auth_url}


@router.get("/google/callback")
def google_callback(request: Request, response: Response, code: str):
    flow = _get_flow()
    flow.redirect_uri = settings.google_redirect_uri
    flow.fetch_token(code=code)
    creds = flow.credentials

    # Decode id_token for basic profile, allow small clock skew
    try:
        idinfo = id_token.verify_oauth2_token(
            creds.id_token,
            google_requests.Request(),
            settings.google_client_id,
            clock_skew_in_seconds=60,  # 👈 allows +/-60s clock skew
        )
    except google_exceptions.InvalidValue as e:
        # If Google still complains, surface a clean error instead of stacktrace
        raise HTTPException(
            status_code=400,
            detail=f"Invalid ID token from Google: {e}"
        )

    user = {
        "id": idinfo.get("sub"),
        "email": idinfo.get("email"),
        "name": idinfo.get("name"),
        "picture": idinfo.get("picture"),
    }

    token_payload = {
        "user": user,
        "google": {
            "access_token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": list(creds.scopes or []),
        },
    }
    session_token = create_access_token(token_payload)

    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=False,  # set True on prod/https
        samesite="lax",
    )

    # redirect to frontend
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = str(settings.frontend_url)
    return response


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("session_token")
    return {"ok": True}


@router.get("/me", response_model=MeResponse)
def me(request: Request):
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {"user": payload["user"]}
