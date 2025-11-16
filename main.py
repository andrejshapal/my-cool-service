import os

from flask_migrate import Migrate, upgrade
from flask_sqlalchemy import SQLAlchemy

from app import models

from app import create_app, db

app = create_app(os.getenv("FLASK_CONFIG") or "default")

migrate = Migrate(app, db)

if __name__ == "__main__":
    app.run()