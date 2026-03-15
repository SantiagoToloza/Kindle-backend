from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/kindle_reader"
    API_SECRET: str = "changeme"  # para proteger el endpoint de ingestión
    APP_BASE_URL: str = "http://localhost:8000"

    class Config:
        env_file = ".env"


settings = Settings()
