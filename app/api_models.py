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

