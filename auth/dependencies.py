from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from auth.auth_handler import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def require_admin(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload or payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access only")
    return payload
    
def require_operator(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload or payload.get("role") != "operator":
        raise HTTPException(status_code=403, detail="Operator access only")
    return payload