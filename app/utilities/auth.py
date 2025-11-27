from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config.config import settings
from app.models.entities.user import User
from app.config.database import get_db
from app.repository.Database.user_repo import UserRepository
import logging

logger = logging.getLogger(__name__)

# This enables Bearer token in Swagger
security = HTTPBearer(auto_error=False)

def create_access_token(data: dict):
    """Create JWT token with expiration"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    logger.info(f"JWT created for user {data.get('sub')} - expires in {settings.ACCESS_TOKEN_EXPIRE_MINUTES} mins")
    return token

# async def get_current_user(
#     credentials: HTTPAuthorizationCredentials = Depends(security),
#     db: Session = Depends(get_db)
# ) -> User:
#     """Validate JWT and return actual user from database"""
#     if not credentials:
#         logger.warning("No Authorization header")
#         raise HTTPException(status_code=401, detail="Authorization header missing")
    
#     token = credentials.credentials
#     try:
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#         user_id: str = payload.get("sub")
#         if not user_id:
#             logger.warning("JWT missing 'sub' claim")
#             raise HTTPException(status_code=401, detail="Invalid token")
        
#         logger.info(f"JWT validated for user {user_id}")
        
#         # To Fetch the actual user from the database
#         user_repo = UserRepository(db)
#         user = user_repo.get_by_id(user_id)
        
#         if not user:
#             logger.warning(f"User not found in database: {user_id}")
#             raise HTTPException(status_code=401, detail="User not found")
        
#         logger.info(f"User found: {user.id} - {user.name}")
#         return user
    
#     except JWTError as e:
#         logger.error(f"JWT validation failed: {e}")
#         raise HTTPException(status_code=401, detail="Invalid token")

from typing import Optional

logger = logging.getLogger(__name__)

# This enables Bearer token in Swagger but makes it optional
security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Validate JWT and return user if authenticated, None if not"""
    if not credentials:
        return None
    
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            return None
        
        logger.info(f"JWT validated for user {user_id}")
        
        # Fetch the actual user from database
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(user_id)
        
        if not user:
            logger.warning(f"User not found in database: {user_id}")
            return None
        
        logger.info(f"User found: {user.id} - {user.name}")
        return user
    
    except JWTError as e:
        logger.error(f"JWT validation failed: {e}")
        return None