# Arquivo criado para garantir os requisitos mínimos de cada atributo

from schema import Schema, fields, validate

class RegisterSchema(Schema):
    email = fields.Email(required = True)
    password = fields.String(required = True, validate = validate.length(min = 8)) #Garante que a senha tem no mínimo 8 caractéres
    full_name = fields.String(required=True)
    role = fields.String(required = True)
    selection_id = fields.String(allow_none = True) # allow_none pois pode ter o auditor sem nenhuma seleção especifíca

class LoginSchema(Schema):
    email = fields.Email(required = True)
    password = fields.String(required = True) 
