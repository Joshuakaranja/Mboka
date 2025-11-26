from marshmallow import Schema, fields, validate, ValidationError


def validate_password(p):
    # Basic password strength: min 8 chars, at least one digit and one letter
    if not p or len(p) < 8:
        raise ValidationError("Password must be at least 8 characters long")
    if not any(c.isdigit() for c in p):
        raise ValidationError("Password must contain at least one digit")
    if not any(c.isalpha() for c in p):
        raise ValidationError("Password must contain at least one letter")


class RegisterSchema(Schema):
    username = fields.Str(
        required=True, validate=validate.Length(min=3, max=120))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate_password)
    role = fields.Str(validate=validate.OneOf(
        ["worker", "client"]), missing="worker")


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class JobCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=3, max=255))
    description = fields.Str(required=True)
    location = fields.Str(required=True)
    price = fields.Float(missing=None)
    location_lat = fields.Float(missing=None)
    location_lng = fields.Float(missing=None)


