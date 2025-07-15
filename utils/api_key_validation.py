from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from config.settings import Settings

security = HTTPBearer()


async def api_key_dependency(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """
    Validate API key from Authorization header
    Expected format: Authorization: Bearer <api_key>
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    api_key = credentials.credentials.strip()
    
    # Check if API key matches expected value
    if api_key != Settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return api_key


def validate_api_key(api_key: Optional[str]) -> bool:
    """
    Validate API key
    """
    if not api_key:
        return False
    
    return api_key.strip() == Settings.API_KEY 