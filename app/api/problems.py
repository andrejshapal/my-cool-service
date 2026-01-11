import datetime

from flask import request, current_app, abort
from flask_jwt_extended import jwt_required, get_jwt
from flask_restx import fields, Resource, Namespace

from app.kafka.producer import producer
from app.models.problems import Problem, Status
from app.managers.problem_manager import get_problems, add_problem, get_problem
from app.schemas.problems import ProblemsSchema, ProblemsUpdateSchema

ns_problems = Namespace('problems', description='Problems related operations')

problems_schema = ProblemsSchema()
update_problems_schema = ProblemsUpdateSchema()

problem_model = ns_problems.model('Problem', {
    'id': fields.String(description="Problem ID"),
    'user_id': fields.Integer(description='User ID'),
    'title': fields.String(description='Problem title'),
    'description': fields.String(description='Problem description'),
    'long': fields.Float(description='Longitude'),
    'lat': fields.Float(description='Latitude'),
    'status': fields.String(attribute='status.value', description='Status (e.g., pending, open)'),  # Access the enum's value directly
    'created_at': fields.DateTime(description='Creation timestamp'),
    'updated_at': fields.DateTime(description='Update timestamp'),
})

problem_model_request = ns_problems.model('ProblemsRequest', {
    'title': fields.String(description='Title', required=True),
    'description': fields.String(description='Description', required=True),
    'long': fields.Float(description='Problem Long'),
    'lat': fields.Float(description='Problem Lat'),
})

problem_model_patch = ns_problems.model('ProblemPatch', {
    'id': fields.String(required=True),
    'title': fields.String(),
    'description': fields.String(),
    'long': fields.Float(),
    'lat': fields.Float(),
    'status': fields.String()
})

@ns_problems.doc(responses={401: 'Not Authorized', 200: 'Success'}, security='Bearer')
@ns_problems.route('/')
class Problems(Resource):
    @jwt_required()
    @ns_problems.marshal_list_with(problem_model, code=200)
    def get(self):
        """Returns problems list as JSON"""
        get_jwt()
        return get_problems()

    @jwt_required()
    @ns_problems.expect(problem_model_request, validate=True)
    @ns_problems.marshal_list_with(problem_model, code=200)
    def post(self):
        claims = get_jwt()
        data = request.get_json()
        try:
            validated_data = problems_schema.load(data)
            problem = Problem(
                user_id=claims.get("sub"),
                title=validated_data.get('title'),
                description=validated_data.get('description'),
                long=validated_data.get('long'),
                lat=validated_data.get('lat'),
                status=Status.Pending,
                created_at=datetime.datetime.now(datetime.UTC),
                updated_at = datetime.datetime.now(datetime.UTC)
            )
            producer.insert_problem(problem)
        except Exception as error:
            current_app.logger.error(error)
            return abort(400, str(error))
        return get_problems()

    @jwt_required()
    @ns_problems.expect(problem_model_patch, validate=True)
    @ns_problems.marshal_list_with(problem_model, code=200)
    def patch(self):
        claims = get_jwt()
        data = request.get_json()
        try:
            validated_data = update_problems_schema.load(data)
            problem = get_problem(validated_data.get('id'))
            if problem is None:
                return abort(403, "Problem with such ID is not found")
            producer.update_problem(validated_data)
        except Exception as error:
            current_app.logger.error(error)
            return abort(400, str(error))
        return get_problems()