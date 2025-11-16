from flask import current_app

from app.models import User

def auth(username, password) -> User | None:
    try:
        user = User.query.filter_by(name=username).first()
    except Exception as error:
        current_app.logger.error(error)
        return None
    if user is not None and user.verify_password(password):
        return user
    return None