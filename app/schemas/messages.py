from marshmallow import Schema, fields, validates, ValidationError

from app.managers.message_manager import get_chat
from app.managers.problem_manager import get_problem


class ChatsBaseSchema(Schema):
    chat_id = fields.UUID(required=True)

    @validates("chat_id")
    def validate_problem_for_message_exists(self, value, **kwargs):
        if get_problem(value) is None:
            raise ValidationError("Problem for provided chatId is not found!")

class ChatsSchema(ChatsBaseSchema):
    message = fields.String(required=True)

class ChatsUpdateSchema(ChatsBaseSchema):
    message_id = fields.String(required=True)
    hidden = fields.Bool(required=True)