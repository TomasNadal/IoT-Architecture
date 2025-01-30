import os
from pathlib import Path

def get_postgres_test_url():
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", 34526)
    password = os.environ.get("DB_PASSWORD", "automisa")  # your password
    user = os.environ.get("DB_USER", "IOT")  # your postgres user
    db_name = os.environ.get("DB_NAME", "iot_dev")  # your database name
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
