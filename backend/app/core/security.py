from functools import lru_cache
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt
from jwt import PyJWKClient
from app.core.config import settings
from app.db import get_db
from app.models import Profile

bearer = HTTPBearer(auto_error=False)

@lru_cache
def _jwks_client():
    if not settings.supabase_url:
        return None
    return PyJWKClient(settings.supabase_url.rstrip("/") + "/auth/v1/.well-known/jwks.json")

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> Profile:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Verified sign-in required")
    if not settings.supabase_url:
        raise HTTPException(status_code=503, detail="Authentication is not configured on this server")
    token = credentials.credentials
    try:
        client = _jwks_client()
        signing_key = client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256", "RS256"],
            audience="authenticated",
            issuer=settings.supabase_url.rstrip("/") + "/auth/v1",
            options={"require": ["exp", "sub"]},
        )
        user_id = str(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")
    profile = db.get(Profile, user_id)
    if profile is None:
        profile = Profile(id=user_id, role="admin" if user_id in settings.admin_ids else "farmer")
        db.add(profile)
        db.commit()
        db.refresh(profile)
    if not profile.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")
    # Admin bootstrap is controlled only by server configuration.
    if user_id in settings.admin_ids and profile.role != "admin":
        profile.role = "admin"
        db.commit()
        db.refresh(profile)
    return profile

def require_admin(user: Profile = Depends(get_current_user)) -> Profile:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Administrator access required")
    return user
