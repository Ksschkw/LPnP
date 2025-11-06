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

# Add these to your existing dependencies.py
from app.repository.Database.service_repo import ServiceRepository
from app.repository.Database.category_repo import CategoryRepository

def get_service_repo(db: Session = Depends(get_db)):
    return ServiceRepository(db)

def get_category_repo(db: Session = Depends(get_db)):
    return CategoryRepository(db)

from app.service.job_service import JobService
from app.service.vouch_service import VouchService

def get_job_service(db: Session = Depends(get_db)):
    return JobService(db)

def get_vouch_service(db: Session = Depends(get_db)):
    return VouchService(db)