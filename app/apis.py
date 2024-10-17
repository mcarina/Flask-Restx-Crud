from flask import request, jsonify
from flask_restx import Resource, Namespace
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity, set_access_cookies, set_refresh_cookies
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
from .api_models import *
from .models import *
from .excel import criar_tabela_dinamica, atualizar_tabela_dinamica
import os
from werkzeug.datastructures import FileStorage
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

authorizations = {
    "jsonWebToken": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization"
    }
}
ns = Namespace("api", authorizations=authorizations)
PASTA_UPLOADS = os.path.join(os.path.dirname(__file__), 'uploads')
    
# permite o usuario fazer login, gerando um token aleatorio
@ns.route("/login") #feito =======================================
class Login(Resource):
    @ns.expect(login_model)
    def post(self):
        cpf = Usuarios.query.filter_by(cpf=ns.payload["cpf"]).first()
        if not cpf:
            return {"error": "Usuário não encontrado"}, 401

        if cpf.nivel_acesso_id == 3:
            return {"error": "Usuário não autorizado para fazer login"}, 401

        if not check_password_hash(cpf.password_hash, ns.payload["password"]):
            return {"error": "Senha incorreta"}, 401

        access_token = create_access_token(identity=cpf.id)
        refresh_token = create_refresh_token(identity=cpf.id)

        resp = jsonify({"access_token": access_token, "refresh_token": refresh_token, "id": cpf.id})

        set_access_cookies(resp, access_token)
        set_refresh_cookies(resp, refresh_token)

        return resp

@ns.route("/refresh") #Não precisa dele no laravel =======================================
class Refresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user)
        return {"access_token": new_access_token}

# dados geral das escolas do estado do amazonas
@ns.route('/escolas') #feito =======================================
class escola(Resource):
    method_decorators = [jwt_required()]
    @ns.doc(security="jsonWebToken")

    @ns.marshal_list_with(escolas_model)
    def get(self):
        return Escolas.query.all() 
    
# api tipo put para api /escolas
@ns.route('/escolas/<int:sigeam>') #feito =======================================
class escola(Resource):
    method_decorators = [jwt_required()]
    @ns.doc(security="jsonWebToken")

    @ns.expect(escolas_model, validate=True)
    def put(self, sigeam):
        data = request.json
        escola = Escolas.query.filter_by(sigeam=sigeam).first()
        if escola:
            for key, value in data.items():
                setattr(escola, key, value)
            db.session.commit()  # Salvando as alterações no banco de dados
            return {'message': 'Escola atualizada com sucesso'}, 200
        else:
            return {'message': 'Escola não encontrada'}, 404
    
# armazenado historico de aprovações
@ns.route('/etapa_hist')#feito =======================================
class hist(Resource):
    method_decorators = [jwt_required()]
    @ns.doc(security="jsonWebToken")
    def get(self):
        try:
            df = pd.read_sql(f'SELECT * FROM hist_space.etapas_aprovacoes_historico', db.engine)
            # Substitui valores NaN por -
            df = df.where(pd.notnull(df), "-")
            dados = df.to_dict(orient="records")
            return jsonify(dados)
        except Exception as e:
            return f"Erro ao obter dados do banco de dados: {str(e)}", 500
        
# api departamento para mapeamento
@ns.route('/dp') #Não precisa dele no laravel =======================================
class dp(Resource):
    method_decorators = [jwt_required()]
    @ns.doc(security="jsonWebToken")

    @ns.marshal_list_with(departamentos_model)
    def get(self):
        return Departamentos.query.all() 
            
# permite o usuario ver a tabelas que foram aprovados 
@ns.route('/dados_escolas_aprovados') #feito =======================================
class dados_escolas(Resource):
    method_decorators = [jwt_required()]
    @ns.doc(security="jsonWebToken")

    @ns.marshal_list_with(tabelas_model)
    def get(self):
        return Tabelas.query.all()

# permite o usuario ver a tabelas que foram aprovados por nome da tabela    
@ns.route('/dados_escolas_aprovados/<string:nome_subtabela>')  #Não precisa dele no laravel =======================================
class dados_escolas(Resource):
    method_decorators = [jwt_required()]
    @ns.doc(security="jsonWebToken")

    def get(self, nome_subtabela):
        tabelanome = Tabelas.query.filter_by(nome_subtabela=nome_subtabela).first()
        
        if tabelanome:
            # Carregar dados do banco de dados
            df = pd.read_sql(f'SELECT * FROM {nome_subtabela}', db.engine)
            
            # Função para formatar a data na coluna '_create'
            def format_date(value):
                if isinstance(value, pd.Timestamp) or isinstance(value, datetime):
                    return value.strftime('%d/%m/%Y %H:%M')
                return value

            # Verificar se a coluna '_create' existe
            if '_create' in df.columns:
                # Aplicar a formatação apenas na coluna '_create'
                df['_create'] = df['_create'].apply(format_date)
            
            # Converter o DataFrame para dicionário e depois para JSON
            dados = df.to_dict(orient="records")
            return jsonify(dados)
        else:
            return {"message": "Tabela não encontrada"}, 404
        
# permite o usuario ver as tabelas com dados releventes, ou nao, de uma tabela que aguarda aprovação
@ns.route('/dados_escolas_aguardando') #feito ======================================= ainda em analise
class dados_escolas_aguardando(Resource):
    method_decorators = [jwt_required()]
    @ns.doc(security="jsonWebToken")

    @ns.marshal_with(etapas_aprovacao_model)
    def get(self):
        return EtapasAprovacoes.query.all()

# permite o usuario ver as tabelas que aguardam aprovação, por nome
@ns.route('/dados_escolas_aguardando/<string:nome_subtabela>') #Não precisa dele no laravel =======================================
class dados_escolas_aguardando(Resource):
    method_decorators = [jwt_required()]
    @ns.doc(security="jsonWebToken")
    
    def get(self, nome_subtabela):
        tabelanome = EtapasAprovacoes.query.filter_by(nome_subtabela=nome_subtabela).first()
        
        if tabelanome:
            df = pd.read_sql(f'SELECT * FROM {nome_subtabela}', db.engine)

            # # Função para formatar a data na coluna '_create'
            # def format_date(value):
            #     if isinstance(value, pd.Timestamp) or isinstance(value, datetime):
            #         return value.strftime('%d/%m/%Y %H:%M')
            #     return value

            # # Verificar se a coluna '_create' existe
            # if '_create' in df.columns:
            #     # Aplicar a formatação apenas na coluna '_create'
            #     df['_create'] = df['_create'].apply(format_date)
            
            # Converter o DataFrame para dicionário e depois para JSON
            dados = df.to_dict(orient="records")
            return jsonify(dados)
        
        else:
            return {"message": "Tabela não encontrada"}, 404
    
# permite /login ver se tal usuario esta no sistema, e kiberar o acesso
@ns.route('/usuarios') #feito =======================================
class nivel_acesso(Resource):
    method_decorators = [jwt_required()]
    @ns.doc(security="jsonWebToken")

    @ns.marshal_list_with(nacesso_model)
    def get(self):
        return NiveisAcesso.query.all() 

# Atualizar o nível de acesso de um usuário
@ns.route('/usuarios/atualizar/<int:id>') #feito =======================================
class UsuarioResource(Resource):
    method_decorators = [jwt_required()]
    
    @ns.doc(security="jsonWebToken")
    @ns.expect(ns.model('NivelAcesso', {'nivel_acesso_id': fields.Integer(required=True)}), validate=True)
    def patch(self, id):
        try:
            user = Usuarios.query.get(id)
            if not user:
                return {'message': 'Usuário não encontrado'}, 404

            data = request.json
            nivel_acesso_id = data.get('nivel_acesso_id')

            # Verifica se o nivel_acesso_id está entre 1 e 4
            if nivel_acesso_id not in {1, 2, 3, 4}:
                return {'message': 'Nível de acesso inválido. Deve ser entre 1 e 4.'}, 400

            user.nivel_acesso_id = nivel_acesso_id

            db.session.commit()

            return {'nivel_acesso_id': user.nivel_acesso_id}, 200
        
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'message': f'Erro no banco de dados: {str(e)}'}, 500

        except Exception as e:
            # Log de erro para diagnosticar o problema
            return {'message': f'Erro interno do servidor: {str(e)}'}, 500

#remover acesso do sistema    
@ns.route('/usuarios/remover_acesso/<int:id>') #feito =======================================
class UsuarioResource(Resource):
    method_decorators = [jwt_required()]
    @ns.doc(security="jsonWebToken")

    # @ns.expect(usuarios_model, validate=True)
    @ns.marshal_with(usuarios_model)
    def put(self, id):
        user = Usuarios.query.get(id)
        if not user:
            return {'message': 'Usuário não encontrado'}, 404

        data = request.json
        if 'nivel_acesso_id' in data:
            user.nivel_acesso_id = data['nivel_acesso_id']

        db.session.commit()

        return user, 200
    
# tras para o lado do cliente os dados do usuario por login (id)
@ns.route('/usuarios/<int:id>') #feito =======================================
class acessar_usuario(Resource):
    method_decorators = [jwt_required()]
    @ns.doc(security="jsonWebToken")   
     
    # @ns.expect(usuarios_model, validate=True)
    @ns.marshal_list_with(usuarios_model)
    def get(self, id):
        # nivel_acesso.nivel_acesso_id = request.json.get('nivel_acesso_id', nivel_acesso.nivel_acesso_id)
        nivel_acesso = Usuarios.query.filter_by(id=id).first()

        if nivel_acesso:
            db.session.commit()
            return nivel_acesso
        else:
            return {"message": "Usuário não encontrado"}, 404

# permite o usuario a solicitar novas informaçõe a serem inseridos no sistema    
@ns.route('/registo_tabela')  #feito =======================================
class etapas_aprovacao(Resource):
    method_decorators = [jwt_required()]
    @ns.doc(security="jsonWebToken")

    @ns.expect(etapas_aprovacao_model, validate=True)
    @ns.marshal_list_with(etapas_aprovacao_model)
    def post(self):
        try:
            hora_local = datetime.now(pytz.timezone('America/Manaus'))
            hora_ajustada = hora_local - timedelta(hours=4)
            # Criar uma nova instância de EtapasAprovacoes a partir dos dados da solicitação
            new_etapa_aprovacao = EtapasAprovacoes(
                nome_subtabela=request.json['nome_subtabela'],
                usuario_id=request.json['usuario_id'],
                departamento_id=request.json['departamento_id'],
                status_aprovacao='pendente',
                created_at=hora_ajustada,
                # created_at=datetime.now(),
                departamento_destino = request.json['departamento_destino'],

            )

            db.session.add(new_etapa_aprovacao)
            db.session.commit()

            return new_etapa_aprovacao

        except FileExistsError as e:
            return{'error':{e}}, 500

# mostrar no lado do front o estado de aprovação que se encontra uma tabela
@ns.route('/etapas_aprovacao') # feito =======================================
class etapas_aprovacao(Resource):
    method_decorators = [jwt_required()]
    @ns.doc(security="jsonWebToken")

    @ns.marshal_list_with(etapas_aprovacao_model)
    def get(self):
        return EtapasAprovacoes.query.order_by(EtapasAprovacoes.id_tabela.desc()).all()

# permite o usuario admin a alterar o status, ver o revisor de informações e enviar uma descrição
@ns.route('/etapas_aprovacao/<int:id_tabela>') # feito =======================================
class etapas_aprovacao_id(Resource):    
    method_decorators = [jwt_required()]
    @ns.doc(security="jsonWebToken")
    
    @ns.expect(etapas_aprovacao_model, validate=True)
    @ns.marshal_list_with(etapas_aprovacao_model)
    def put(self, id_tabela):
        etapa_aprovacao = EtapasAprovacoes.query.get(id_tabela)
        etapa_aprovacao.status_aprovacao = request.json.get('status_aprovacao', etapa_aprovacao.status_aprovacao)
        etapa_aprovacao.descricao = request.json.get('descricao', etapa_aprovacao.descricao)
        etapa_aprovacao.revisor = request.json.get('revisor', etapa_aprovacao.revisor)

        db.session.commit()
        return etapa_aprovacao

# upload do excel file feito pelo usuario
@ns.route('/upload') #feito =======================================
class UploadArquivo(Resource):
    method_decorators = [jwt_required()]
    @ns.doc(security="jsonWebToken")

    @api.expect(api.parser().add_argument('file', type=FileStorage, location='files'))
    def post(self):
        arquivo = request.files['file']
        if arquivo:
            if arquivo.filename.endswith('.xlsx'):
                # Salva o arquivo
                caminho_arquivo = os.path.join(PASTA_UPLOADS, arquivo.filename)
                arquivo.save(caminho_arquivo)

                # Ler o arquivo Excel
                df = pd.read_excel(caminho_arquivo)
                nome_tabela = os.path.splitext(os.path.basename(caminho_arquivo))[0]
                
                # Chama a função para criar ou atualizar a tabela e captura a mensagem
                mensagem, status_code = criar_tabela_dinamica(df, nome_tabela)

                # Remove o arquivo após o processamento
                os.remove(caminho_arquivo)

               # Retorna a mensagem com o código de status apropriado
                return {'mensagem': mensagem}, status_code
            else:
                return {'mensagem': 'O arquivo deve estar no formato XLSX'}, 400
        else:
            return {'mensagem': 'Nenhum arquivo carregado'}, 400
        
# atualizar upload do excel file feito pelo usuario
@ns.route('/upload_atualizar') #feito =======================================
class UploadArquivo(Resource):
    method_decorators = [jwt_required()]
    @ns.doc(security="jsonWebToken")

    @api.expect(api.parser().add_argument('file', type=FileStorage, location='files'))
    def post(self):
        arquivo = request.files['file']
        if arquivo:
            
            if arquivo.filename.endswith('.xlsx'):
                # Salva o arquivo
                caminho_arquivo = os.path.join(PASTA_UPLOADS, arquivo.filename)
                arquivo.save(caminho_arquivo)

                df = pd.read_excel(caminho_arquivo)
                nome_tabela = os.path.splitext(os.path.basename(caminho_arquivo))[0]
                
                atualizar_tabela_dinamica(df, nome_tabela)

                os.remove(caminho_arquivo)

                return {'mensagem': 'Arquivo carregado com sucesso'}, 201
            else:
                return {'mensagem': 'O arquivo deve estar no formato XLSX'}, 400
        else:
            return {'mensagem': 'Nenhum arquivo carregado'}, 400

# permite o usuario admin a adicionar novos usuarios ao sistema  
@ns.route('/registros_usuarios') #feito =======================================
class RegistroUsuarios(Resource):
    method_decorators = [jwt_required()]
    @ns.doc(security="jsonWebToken")

    @ns.expect(registro_model)
    # @ns.marshal_with(usuarios_model)
    def post(self):
        try:
            email = ns.payload["email"]
            cpf = ns.payload["cpf"]
            nome = ns.payload["nome"]
            departamento = ns.payload["departamento"]
            nivel_acesso_id = ns.payload["nivel_acesso_id"]
            password = ns.payload["password"]
            password_hash = generate_password_hash(password)

            errors = {}

            if Usuarios.query.filter_by(email=email).first():
                errors["email"] = "Email já cadastrado"
            
            if Usuarios.query.filter_by(cpf=cpf).first():
                errors["cpf"] = "CPF já cadastrado"

            if errors:
                return {"errors": errors}, 400

            # Crie um novo usuário
            novo_usuario = Usuarios(
                email=email,
                cpf=cpf,
                nome=nome,
                departamento=departamento,
                nivel_acesso_id=nivel_acesso_id,
                password_hash=password_hash
            )

            db.session.add(novo_usuario)
            db.session.commit()

            return novo_usuario.to_dict(), 201

        except Exception as e:
            print(f"Erro durante o registro de usuários: {str(e)}")
            return {"message": "Internal Server Error"}, 500
