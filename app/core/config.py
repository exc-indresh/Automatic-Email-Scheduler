from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URI: str
    MONGODB_DB: str
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str
    SMTP_FROM: str
    API_CONTENT_URL: str
    DEFAULT_TZ: str

    class Config:
        env_file = ".env.example"


settings = Settings()