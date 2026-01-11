from flask import request, current_app, abort
from flask_jwt_extended import jwt_required, get_jwt
from flask_restx import fields, Resource, Namespace

from app.extensions import db
from app.models.users import User
from app.schemas.user import UserRequestSchema

ns_users = Namespace('users', description='Users related operations')

user_schema = UserRequestSchema()

user_model_response = ns_users.model('UserResponse', {
    'name': fields.String(description='Username'),
    'email': fields.String(description='Email address')
})

user_model_request = ns_users.model('UserRequest', {
    'name': fields.String(description='Username', required=True),
    'email': fields.String(description='Email address', required=True),
    'role': fields.String(description='Admin or editor', required=True),
    'password': fields.String(description='User password', required=True)
})

@ns_users.doc(responses={401: 'Not Authorized', 200: 'Success'}, security='Bearer')
@ns_users.route('/')
class Users(Resource):
    @jwt_required()
    @ns_users.marshal_list_with(user_model_response, code=200)
    def get(self):
        """Returns user list as JSON"""
        # get_jwt()
        return User.query.all()

    @jwt_required()
    @ns_users.marshal_with(user_model_response, code=200)
    @ns_users.expect(user_model_request, validate=True)
    def post(self):
        claims = get_jwt()
        if claims['role'] != 'admin':
            abort(401)
        data = request.get_json()
        try:
            validated_data = user_schema.load(data)
            user = User(
                name=validated_data.get('name') if validated_data.get('name') else "",
                email=validated_data.get('email') if validated_data.get('email') else "",
                password=validated_data.get('password') if validated_data.get('password') else "",
                role_name=validated_data.get('role') if validated_data.get('role') else "editor"
            )
            db.session.add(user)
            db.session.commit()
        except Exception as error:
            current_app.logger.error(error)
            return abort(400, str(error))
        return user
