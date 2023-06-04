import logging
import os


class Config:
    API_V1_STR = "/api/v1_0_0"
    PROJECT_NAME = "jobSearcher"


class DevelopmentConfig(Config):
    DATABASE_URL = os.getenv("DATABASE_URL", "bolt://127.0.0.1:7687")
    SECRET_KEY = os.getenv("SECRET_KEY","my-very-secret-dev-key")
    HOST = "localhost"
    PORT = 8000
    LOG_LEVEL = logging.DEBUG
    DATABASE_PASS = os.getenv("DATABASE_PASS", "password123")
    DATABASE_USER = "neo4j"
    DATABASE_PORT = 27017


class ProductionConfig(Config):
    DATABASE_URL = "localhost"
    SECRET_KEY = "my-very-secret-prod-key"
    DATABASE_PORT = 27017
    HOST = "localhost"
    PORT = 8000
    LOG_LEVEL = logging.INFO
    DATABASE_PASS = "example"
    DATABASE_USER = "root"


class WeWorkRemotelyConfig(Config):
    CSV_FILE_NAME = "jobs.csv"
    BASE_URL = "https://weworkremotely.com"
    REGEX_FOR_CATEGORIES = r'<a href="(/[^"]*)">View all[^<]*</a>'
    REGEX_FOR_JOBS = r'<a href="(/[^"]*)">'


ENV = os.getenv("MY_APP_ENV", "development")

if ENV == "development":
    config = DevelopmentConfig()
elif ENV == "production":
    config = ProductionConfig()
else:
    raise ValueError(f"Unknown environment {ENV}")
