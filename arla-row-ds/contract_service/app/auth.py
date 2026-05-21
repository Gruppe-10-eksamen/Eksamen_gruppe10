"""
Simpel API-nøgle-autentificering. Klienten skal sende headeren:
    X-API-Key: <nøgle>
Nøglen sammenlignes med den konfigurerede API_KEY. I produktion kommer
nøglen fra et secret, aldrig fra koden.

Dette er bevidst simpelt for en MVP. I rapporten kan I beskrive at en
produktionsløsning ville bruge OAuth2/JWT via Azure AD i stedet.
"""
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from app.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(api_key: str = Security(api_key_header)) -> str:
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ugyldig eller manglende API-nøgle",
        )
    return api_key
