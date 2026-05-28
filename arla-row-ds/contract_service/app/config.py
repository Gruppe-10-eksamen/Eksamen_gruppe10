"""
Konfiguration fra environment variables. Secrets injiceres via .env lokalt og GitHub Secrets i produktion.
"""
import os


class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://arla:arla@postgres:5432/arla_row",
    )
    API_KEY: str = os.getenv("API_KEY", "dev-contract-key")
    SERVICE_NAME: str = "contract-service"


settings = Settings()
