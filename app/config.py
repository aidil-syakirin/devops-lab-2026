import os

DB_USERNAME = os.environ.get('DB_USERNAME', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME', 'db')
DB_HOSTNAME = os.environ.get('DB_HOSTNAME')

class Config:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOSTNAME}:5432/{DB_NAME}"
    )
