from marshmallow import Schema, fields


class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)


class SignUpSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    country = fields.Str(required=True)