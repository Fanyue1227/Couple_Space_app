from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "情侣小站"
    SECRET_KEY: str = "your-super-secret-key-change-it"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    
    # Database
    DATABASE_URL: str = "mysql+pymysql://root:root@localhost:3306/qlxz_app?charset=utf8mb4"
    
    # Storage - Use Absolute Path to avoid CWD issues
    UPLOAD_DIR: str = "/www/wwwroot/qlxz_backend/static/uploads"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
