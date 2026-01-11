from marshmallow import Schema, fields
from marshmallow.validate import Length

from app.models.problems import Status


class ProblemsSchema(Schema):
    title = fields.String(required=True,  validate=[Length(min=5, max=255)])
    description = fields.String(required=True, validate=[Length(min=20, max=500)])
    long = fields.Decimal(places=6)
    lat = fields.Decimal(places=6)
    status = fields.Enum(Status, allow_none=True, by_value=True)

class ProblemsUpdateSchema(Schema):
    id = fields.UUID(required=True)
    title = fields.String(validate=[Length(min=5, max=255)], required=False)
    description = fields.String(validate=[Length(min=20, max=500)], required=False)
    long = fields.Decimal(places=6)
    lat = fields.Decimal(places=6)
    status = fields.Enum(Status, allow_none=True, by_value=True)