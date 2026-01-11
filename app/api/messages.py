from flask import request, current_app, abort
from flask_jwt_extended import jwt_required, get_jwt
from flask_restx import fields, Resource, Namespace

from app.kafka.producer import producer
from app.managers.message_manager import add_message, get_chat, get_message
from app.models.messages import Message
from app.managers.problem_manager import get_problems
from app.schemas.messages import ChatsUpdateSchema, ChatsSchema, ChatsBaseSchema

ns_chats = Namespace('chats', description='Chats related operations')

chats_schema = ChatsSchema()
chats_base_schema = ChatsBaseSchema()
update_chats_schema = ChatsUpdateSchema()

chat_model = ns_chats.model('Problem', {
    'chat_id': fields.String(description="Chat ID"),
    'message_id': fields.String(description="Message ID"),
    'author': fields.Integer(description='Message Author'),
    'rating': fields.Integer(description='Rating'),
    'message': fields.String(description='Message'),
    'created_at': fields.DateTime(description='Creation timestamp'),
    'hidden': fields.Boolean(description='Hide from users'),
})

chat_model_get = ns_chats.model('ChatGet', {
    'chat_id': fields.String(description='Chat ID', required=True),
})

chat_model_request = ns_chats.model('ChatRequest', {
    'chat_id': fields.String(description='Chat ID', required=True),
    'message': fields.String(description='Message', required=True),
})

chat_model_patch = ns_chats.model('ChatPatch', {
    'chat_id': fields.String(description='Chat ID', required=True),
    'message_id': fields.String(description='Message ID', required=True),
    'hidden': fields.Boolean(description='Hide from users', required=True),
})

chat_get_parser = ns_chats.parser()
chat_get_parser.add_argument("chat_id", type=str, required=True, location="args")

@ns_chats.doc(responses={401: 'Not Authorized', 200: 'Success'}, security='Bearer')
@ns_chats.route('/')
class Messages(Resource):
    @jwt_required()
    @ns_chats.expect(chat_get_parser, validate=True)
    @ns_chats.marshal_list_with(chat_model, code=200)
    def get(self):
        """Returns messages list as JSON"""
        get_jwt()
        chat_id = request.args.get("chat_id")
        try:
            chat = get_chat(chat_id)
            if not chat:
                return abort(403, "Chat with such ID is not found")
            return chat
        except Exception as error:
            current_app.logger.error(error)
            return abort(400, str(error))

    @jwt_required()
    @ns_chats.expect(chat_model_request, validate=True)
    @ns_chats.marshal_list_with(chat_model, code=200)
    def post(self):
        claims = get_jwt()
        data = request.get_json()
        try:
            validated_data = chats_schema.load(data)
            chat = Message(
                chat_id=validated_data.get('chat_id'),
                author=claims.get("sub"),
                message=validated_data.get('message'),
            )
            producer.insert_message(chat)
        except Exception as error:
            current_app.logger.error(error)
            return abort(400, str(error))
        return get_chat(validated_data.get('chat_id'))

    @jwt_required()
    @ns_chats.expect(chat_model_patch, validate=True)
    @ns_chats.marshal_list_with(chat_model, code=200)
    def patch(self):
        claims = get_jwt()
        data = request.get_json()
        try:
            validated_data = update_chats_schema.load(data)
            producer.update_message(validated_data)
        except Exception as error:
            current_app.logger.error(error)
            return abort(400, str(error))
        return get_chat(validated_data.get('chat_id'))