import os


class Config:
    DEBUG = False

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///my_cool_service.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OPA_HOST = os.environ.get("OPA_HOST", "localhost")
    OPA_PORT = os.environ.get("OPA_PORT", 8181)

    ADMIN_PASS = os.environ.get("ADMIN_PASS", "12345")

config_by_name = dict(
    default=ProductionConfig,
)