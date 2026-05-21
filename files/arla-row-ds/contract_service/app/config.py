"""
Konfiguration læses fra environment variables (12-factor app-princippet).
Aldrig hardcode hemmeligheder i koden — de kommer fra .env lokalt og fra
GitHub Secrets / cloud-miljøet i produktion.
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
