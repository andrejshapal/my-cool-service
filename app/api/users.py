from functools import wraps

from flask import request, current_app, abort
from flask_restx import fields, Resource, Namespace

from app.extensions import db
from app.auth import auth
from app.models import User
from app.opa import OpaValidator
from app.schema import UserRequestSchema

ns = Namespace('users', description='Users related operations')

user_schema = UserRequestSchema()

user_model_response = ns.model('UserResponse', {
    'name': fields.String(description='Username'),
    'email': fields.String(description='Email address')
})

user_model_request = ns.model('UserRequest', {
    'name': fields.String(description='Username', required=True),
    'email': fields.String(description='Email address', required=True),
    'role': fields.String(description='Admin or editor', required=True),
    'password': fields.String(description='User password', required=True)
})

def basic_auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        login_data = request.authorization
        path = request.path
        method = request.method
        if login_data:
            user = auth(login_data.get('username'), login_data.get('password'))
            if user:
                o = OpaValidator()
                if o.validate_call(user.name, user.email, user.role_name, method, path):
                    return f(*args, **kwargs)
                abort(401, "Failed to validate user role")
        current_app.logger.error("Unauthorized access attempt")
        abort(401, "Failed authentication")
    return wrapper

@ns.doc(responses={401: 'Not Authorized', 200: 'Success'}, security='basicAuth')
@ns.route('/')
class Users(Resource):
    method_decorators = [basic_auth_required]
    @ns.marshal_list_with(user_model_response, code=200)
    def get(self):
        """Returns user list as JSON"""
        return User.query.all()

    @ns.marshal_with(user_model_response, code=200)
    @ns.expect(user_model_request, validate=True)
    def post(self):
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
