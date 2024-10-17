from .models import *
from .api_models import *
from flask import request
from sqlalchemy.exc import SQLAlchemyError
from flask_restx import Resource, Namespace
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity, set_access_cookies, set_refresh_cookies


authorizations = {
    "jsonWebToken": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization"
    }
}
ns = Namespace("api", authorizations=authorizations)
    

@ns.route("/login")
class Login(Resource):
    @ns.expect(login_model)
    def post(self):
        data = request.json
        email = data.get("email")
        password = data.get("password")

        usuario = Usuarios.query.filter_by(email=email).first()

        if not usuario:
            return {"message": "Email ou senha incorretos."}, 401

        if not check_password_hash(usuario.password_hash, password):
            return {"message": "Email ou senha incorretos."}, 401

        return {
            "message": "Login bem-sucedido",
            # "token": token,
            "usuario": usuario.to_dict()
        },

@ns.route('/usuarios') 
class ReadUsuarios(Resource):
    method_decorators = [jwt_required()]
    @ns.doc(security="jsonWebToken")

    @ns.marshal_list_with(usuarios_model )
    def get(self):
        return Usuarios.query.all() 


@ns.route('/usuario-update/<int:id>')
class UsuarioUpdate(Resource):
    method_decorators = [jwt_required()]
    
    @ns.doc(security="jsonWebToken")
    @ns.expect(usuario_update_model, validate=True) 
    def patch(self, id):

        usuario = Usuarios.query.get_or_404(id)

        data = request.json

        if 'email' in data:
            usuario.email = data['email']
        if 'nome' in data:
            usuario.nome = data['nome']
        if 'password' in data:
            usuario.password_hash = generate_password_hash(data['password'])
        if 'nivel_acesso_id' in data:
            usuario.nivel_acesso_id = data['nivel_acesso_id']

        try:
            db.session.commit()
            return {"message": "Usuário atualizado com sucesso"}, 200
        except Exception as e:
            db.session.rollback()
            return {"message": "Erro ao atualizar usuário", "error": str(e)}, 500


@ns.route('/usuarios/<int:id>') 
class UsuarioId(Resource):
    method_decorators = [jwt_required()]

    @ns.doc(security="jsonWebToken")
    @ns.marshal_with(usuarios_model) 
    def get(self, id):

        user = Usuarios.query.filter_by(id=id).first()

        if user:
            return user 
        else:
            return {"message": "Usuário não encontrado"}, 404 


@ns.route('/registros_usuarios') 
class CreateUsuarios(Resource):
    method_decorators = [jwt_required()]
    @ns.doc(security="jsonWebToken")

    @ns.expect(registro_model)  # Espera os dados de registro no modelo
    @ns.marshal_with(usuarios_model)  # Retorna os dados no formato do modelo de usuário
    def post(self):
        try:
            # Extrair os dados da requisição
            email = ns.payload.get("email")
            nome = ns.payload.get("nome")
            password = ns.payload.get("password")

            # Gerar o hash da senha
            password_hash = generate_password_hash(password)

            errors = {}

            # Validações
            if Usuarios.query.filter_by(email=email).first():
                errors["email"] = "Email já cadastrado"

            if errors:
                return {"errors": errors}, 400

            # Criar um novo usuário
            novo_usuario = Usuarios(
                email=email,
                nome=nome,
                password_hash=password_hash
            )

            # Adicionar e salvar no banco de dados
            db.session.add(novo_usuario)
            db.session.commit()

            # Retornar o usuário criado
            return novo_usuario.to_dict(), 201

        except Exception as e:
            print(f"Erro durante o registro de usuários: {str(e)}")
            return {"message": "Internal Server Error"}, 500