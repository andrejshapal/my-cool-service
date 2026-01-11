from flask import request, current_app, jsonify
from flask_jwt_extended import create_access_token
from flask_restx import Namespace, fields, Resource, abort

from app.auth import auth

ns_auth = Namespace('auth', description='Auth related operations')

auth_model_response = ns_auth.model('AuthResponse', {
    'user_id': fields.String(description='UserId'),
    'token': fields.String(description='Session JWT Token')
})

@ns_auth.doc(responses={401: 'Not Authorized', 200: 'Success'}, security='Basic')
@ns_auth.route('/')

class Users(Resource):
    @ns_auth.marshal_list_with(auth_model_response, code=200)
    def get(self):
        """Returns user session JWT token"""
        login_data = request.authorization
        try:
            user = auth(login_data.get('username'), login_data.get('password'))
            return {
            "user_id": user.id,
            "token": create_access_token(identity=str(user.id), additional_claims=user.jwt_claims())
        }
        except Exception as error:
            current_app.logger.error(f"Unauthorized access attempt: {error}")
            abort(401, "Failed authentication")
