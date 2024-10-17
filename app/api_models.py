from flask_restx import fields, Model
from datetime import datetime
from .extensions import api


login_model = api.model( "login", {
    "cpf": fields.Integer,
    "password": fields.String
})

usuarios_model = api.model("Usuarios", {
    "id": fields.Integer,
    "email": fields.String, 
    "nome": fields.String,
    "password_hash": fields.String(required=True, description='Hashed Password', write_only=True),

})

registro_model = api.model("Registro", {
    "email": fields.String(required=True),
    "cpf": fields.String(required=True),
    "nome": fields.String(required=True),
    "departamento": fields.Integer(required=True),
    "nivel_acesso_id": fields.Integer(required=True),
    "password": fields.String(required=True),
 
})
