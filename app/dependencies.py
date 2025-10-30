from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db

# === USER SERVICE ===
from app.service.user_service import UserService

class UserServiceDependency:
    def __call__(self, db: Session = Depends(get_db)) -> UserService:
        return UserService(db)

get_user_service = UserServiceDependency()


# === SERVICE SERVICE ===
from app.service.service_service import ServiceService

class ServiceServiceDependency:
    def __call__(self, db: Session = Depends(get_db)) -> ServiceService:
        return ServiceService(db)

get_service_service = ServiceServiceDependency()