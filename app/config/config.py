import os
from dotenv import load_dotenv


load_dotenv()  

class Settings:
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:Kosi%%40Postgre@localhost:5432/locale_db")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "theboywhoplayedtheharp")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # # External APIs
    # QOREID_API_KEY: str = os.getenv("QOREID_API_KEY", "")
    # QOREID_SECRET: str = os.getenv("QOREID_SECRET", "")
    
    # # App Settings
    # DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

settings = Settings()
