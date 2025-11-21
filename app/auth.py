from fastapi import Header, HTTPException, Depends
from app.config import settings

def get_api_token(authorization: str | None = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    scheme, _, token = authorization.partition(" ")
    if token != settings.API_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid API token")
    return token
