import os
from functools import lru_cache

class Settings:
    def __init__(self) -> None:

        self.database_url = "mysql+pymysql://Iliaz:root@127.0.0.1:3306/railway"
        
        self.secret_key = os.getenv("SECRET_KEY", "change-me-in-production")
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.refresh_token_expire_days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
        self.refresh_cookie_secure = os.getenv("REFRESH_COOKIE_SECURE", "false").lower() == "true"

@lru_cache
def get_settings() -> Settings:
    return Settings()

