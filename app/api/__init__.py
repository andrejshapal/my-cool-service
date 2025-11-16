from flask_restx import Api
from flask import Blueprint

from app.api.users import ns

authorizations = {
    'basicAuth': {
        'type': 'basic'
    }
}

api_bp = Blueprint("api", __name__)

api = Api(api_bp, authorizations=authorizations, apiVersion='0.1')

api.add_namespace(ns)