from marshmallow import Schema, fields, validates, ValidationError
from marshmallow.validate import Length

from app.models import User

class UserRequestSchema(Schema):
    name = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=[Length(min=5, max=128)])
    role = fields.String(required=True)

    @validates("name")
    def validate_unique_username(self, value, **kwargs):
        if User.query.filter_by(name=value).first():
            raise ValidationError("Name must be unique.")

    @validates("email")
    def validate_unique_email(self, value, **kwargs):
        if User.query.filter_by(email=value).first():
            raise ValidationError("Email must be unique.")
