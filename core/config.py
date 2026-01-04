from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Lexi Platform API"
    DEBUG: bool = True

    FIREBASE_CREDENTIALS_PATH: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_DAYS: int = 7

    DATABASE_URL: str

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()