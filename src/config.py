import os
from pathlib import Path
from datetime import timedelta
from os import environ

JWT_SECRET = environ.get('JWT_SECRET', 'your-consistent-secret-key')

def get_postgres_uri():
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", 34526)
    password = os.environ.get("DB_PASSWORD", "automisa")  # your password
    user = os.environ.get("DB_USER", "IOT")  # your postgres user
    db_name = os.environ.get("DB_NAME", "iot_dev") 
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

def get_jwt_secret():
    return JWT_SECRET

def get_app_secret():
    return os.environ.get('SECRET_KEY', 'dev-secret-key')

def get_cors_origins():
    return os.environ.get('CORS_ORIGINS', 'http://localhost:5173').split(',')

def get_token_expiry():
    days = int(os.environ.get('TOKEN_EXPIRY_DAYS', 1))
    return timedelta(days=days)

class Config:
    SECRET_KEY = get_app_secret()
    JWT_SECRET_KEY = get_jwt_secret()
    JWT_ACCESS_TOKEN_EXPIRES = get_token_expiry()
    SQLALCHEMY_DATABASE_URI = get_postgres_uri()
    CORS_ORIGINS = get_cors_origins()
