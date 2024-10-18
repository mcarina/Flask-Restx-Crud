from flask_restx import fields, Model
from datetime import datetime
from .extensions import api


login_model = api.model( "login", {
    "email": fields.String,
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
    "nome": fields.String(required=True),
    "password": fields.String(required=True), 
})

usuario_update_model = api.model("UsuarioUpdate", {
    "email": fields.String(description="Email do usuário", required=False),
    "nome": fields.String(description="Nome do usuário", required=False),
    "password": fields.String(description="Nova senha do usuário", required=False),
})