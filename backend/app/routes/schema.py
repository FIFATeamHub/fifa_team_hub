import uuid
from marshmallow import Schema, fields, validate, validates, ValidationError
from app.extensions import db
from app.models.selection import Selection

class RegisterSchema(Schema):
    email = fields.Email(required = True)
    password = fields.String(required = True, validate = validate.Length(min = 8)) #Garante que a senha tem no mínimo 8 caractéres
    full_name = fields.String(required=True)
    selection_id = fields.String(required = True)

    @validates("selection_id")
    def validate_selection_exists(self, value, **kwargs):
        try:
            selection_uuid = uuid.UUID(str(value))
        except (ValueError, TypeError, AttributeError):
            raise ValidationError("selection_id inválido.")

        if not db.session.get(Selection, selection_uuid):
            raise ValidationError("Seleção informada não existe.")

class LoginSchema(Schema):
    email = fields.Email(required = True)
    password = fields.String(required = True) 
