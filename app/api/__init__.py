from flask_jwt_extended.exceptions import JWTExtendedException
from flask_restx import Api
from flask import Blueprint, current_app, jsonify
from jwt import PyJWTError

from app.api.auth import ns_auth
from app.api.messages import ns_chats
from app.api.problems import ns_problems
from app.api.users import ns_users
from app.api import socket

authorizations = {
    'Basic': {
        'type': 'basic'
    },
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

api_bp = Blueprint("api", __name__)

api = Api(api_bp, authorizations=authorizations, apiVersion='0.1', errors=False)

api.add_namespace(ns_auth)
api.add_namespace(ns_users)
api.add_namespace(ns_problems)
api.add_namespace(ns_chats)


@api.errorhandler(JWTExtendedException)
def handle_jwt_exceptions(error):
    return {'message': str(error)}, getattr(error, 'code', 401)
@api.errorhandler(PyJWTError)
def handle_pyjwt_exceptions(error):
    return {'message': str(error)}, getattr(error, 'code', 401)