# app/routes/admin_routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.repository.Database.category_repo import CategoryRepository
from app.models.entities.serviceCategory import ServiceCategory
import logging
from dotenv import load_dotenv
import os
load_dotenv()

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/categories", tags=["admin"])

# Move to .env later
ADMIN_KEY = os.getenv("ADMIN_KEY")

from app.repository.Database.user_repo import UserRepository
from app.models.entities.user import User
from app.models.Responses.user_responses import UserDetailResponse
from typing import List


def require_admin_key(admin_key: str = Query(..., description="Admin access key")):
    """Validate admin key — REQUIRED IN QUERY"""
    if admin_key != ADMIN_KEY:
        logger.warning(f"ADMIN ACCESS DENIED: Wrong key '{admin_key}'")
        raise HTTPException(status_code=403, detail="Invalid admin key")
    logger.info(f"ADMIN ACCESS GRANTED: Key accepted")
    return True

# === CATEGORY ENDPOINTS (VISIBLE IN SWAGGER) ===
@router.post("/categories")
def create_category(
    name: str,
    description: str = None,
    db: Session = Depends(get_db),
    key = Depends(require_admin_key)
):
    """ADMIN: Create a service category"""
    repo = CategoryRepository(db)
    if repo.get_by_name(name):
        logger.warning(f"Admin duplicate category attempt: {name}")
        raise HTTPException(400, "Category already exists")
    category = repo.create(name=name, description=description)
    logger.info(f"ADMIN: Created category '{name}' (ID: {category.id})")
    return {"id": category.id, "name": category.name}

@router.get("/categories", response_model=List[dict])
def list_categories(db: Session = Depends(get_db), key = Depends(require_admin_key)):
    """ADMIN: List all categories"""
    repo = CategoryRepository(db)
    cats = repo.get_all()
    logger.info(f"ADMIN: Listed {len(cats)} categories")
    return [{"id": c.id, "name": c.name} for c in cats]

# === FULL USER DATA ENDPOINT (VISIBLE, ALL FIELDS) ===
@router.get("/users", response_model=List[UserDetailResponse])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    key = Depends(require_admin_key)
):
    """
    ADMIN ONLY: Get ALL user data
    - Requires admin_key in query
    - Returns EVERY field
    """
    logger.info(f"ADMIN: Fetching ALL user data (skip={skip}, limit={limit})")
    repo = UserRepository(db)
    users = repo.get_all(skip=skip, limit=limit)
    
    if not users:
        logger.info("ADMIN: No users found")
        return []
    
    logger.info(f"ADMIN: Returned FULL data for {len(users)} users")
    return [UserDetailResponse.model_validate(user) for user in users]