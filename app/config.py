import os

class Config:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://appuser:apppass@postgres-db:5432/appdb"
    )
