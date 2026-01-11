import os

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app import models, socketio

from app import create_app, db
from app.kafka.consumer import start_consumer

app = create_app(os.getenv("FLASK_CONFIG") or "default")

migrate = Migrate(app, db)

if os.getenv("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
    start_consumer(app)

if __name__ == "__main__":
    socketio.run(app)
