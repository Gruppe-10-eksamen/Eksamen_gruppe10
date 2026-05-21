import os


class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://arla:arla@postgres:5432/arla_row",
    )
    API_KEY: str = os.getenv("API_KEY", "dev-order-key")
    # URL til Contract Service (intern service-til-service kommunikation)
    CONTRACT_SERVICE_URL: str = os.getenv(
        "CONTRACT_SERVICE_URL", "http://contract-service:8001"
    )
    CONTRACT_SERVICE_API_KEY: str = os.getenv(
        "CONTRACT_SERVICE_API_KEY", "dev-contract-key"
    )
    SERVICE_NAME: str = "order-service"


settings = Settings()
