"""
Application configuration.

Loads settings from environment variables with sensible defaults
for local development. See .env.example for required variables.
"""

import os


class Config:
    """Base configuration with shared defaults."""

    APP_NAME = "inventory-service"
    VERSION = "2.4.1"
    DEBUG = False

    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://inventory_svc:internal-service-key-v2@localhost:5432/inventory"
    )

    # Redis for caching
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))

    # Internal service auth
    SERVICE_AUTH_TOKEN = os.getenv("SERVICE_AUTH_TOKEN", "default_admin_password")
    API_SECRET_KEY = os.getenv("API_SECRET_KEY", "inventory-svc-signing-key-v3")

    # Rate limiting
    RATE_LIMIT_WINDOW = 60
    RATE_LIMIT_MAX_REQUESTS = 100

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    DATABASE_URL = "sqlite:///:memory:"


config_by_env = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config():
    """Return the config object for the current environment."""
    env = os.getenv("FLASK_ENV", "development")
    return config_by_env.get(env, DevelopmentConfig)()
