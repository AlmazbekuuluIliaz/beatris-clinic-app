import os
from functools import lru_cache

DEFAULT_DATABASE_URL = "mysql+pymysql://Iliaz:root@127.0.0.1:3306/beatris?charset=utf8mb4"


class Settings:
    def __init__(self) -> None:
        database_url = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL).strip()
        if database_url.startswith("mysql://"):
            database_url = database_url.replace("mysql://", "mysql+pymysql://", 1)
        self.database_url = database_url
        self.secret_key = os.getenv("SECRET_KEY", "change-me-in-production")
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.refresh_token_expire_days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
        self.refresh_cookie_secure = os.getenv("REFRESH_COOKIE_SECURE", "false").lower() == "true"


@lru_cache
def get_settings() -> Settings:
    return Settings()

