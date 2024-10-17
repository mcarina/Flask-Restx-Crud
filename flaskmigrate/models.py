from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt
import pytz

from dotenv import load_dotenv
import os


load_dotenv()
app = Flask(__name__)
# uri_modificada = os.getenv('URI')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('URI')
db = SQLAlchemy(app)

class NiveisAcesso(db.Model):
    __tablename__ = 'niveis_acesso'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(20), nullable=False)
    usuarios = db.relationship('Usuarios', backref='niveis_acesso', lazy=True)

class Usuarios(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    departamento = db.Column(db.Integer, nullable=False)
    nivel_acesso_id = db.Column(db.Integer, db.ForeignKey('niveis_acesso.id'), nullable=False)
    rotinas = db.relationship('Rotinas', secondary='usuarios_rotinas', backref='usuarios')
    password_hash = db.Column(db.Text)
    reset_token = db.Column(db.String(100))
    reset_token_expires = db.Column(db.DateTime)  

    def check_password(self, password_hash):
        return bcrypt.checkpw(password_hash.encode('utf-8'), self.password.encode('utf-8'))

    def to_dict(self):
        return {
            "email": self.email,
            "cpf": self.cpf,
            "nome": self.nome,
            "departamento": self.departamento,
            "nivel_acesso_id": self.nivel_acesso_id,
            # Adicione outros campos se necessário
        }   

class Rotinas(db.Model):
    __tablename__ = 'rotinas'
    id = db.Column(db.Integer, primary_key=True)
    descricao_rotina = db.Column(db.String(255), nullable=False)
    nivel_acesso_id = db.Column(db.Integer, db.ForeignKey('niveis_acesso.id'), nullable=False)

class Departamentos(db.Model):
    __tablename__ = 'departamentos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_depart = db.Column(db.String(255), nullable=False)

class UsuariosRotina(db.Model):
    __tablename__ = 'usuarios_rotinas'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    rotina_id = db.Column(db.Integer, db.ForeignKey('rotinas.id'), nullable=False)
    nivel_acesso_id = db.Column(db.Integer, db.ForeignKey('niveis_acesso.id'), nullable=False)
    departamento = db.Column(db.Integer, db.ForeignKey('departamentos.id'), nullable=False)

class EtapasAprovacoes(db.Model):
    __tablename__ = 'etapas_aprovacoes'
    id_tabela = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_subtabela = db.Column(db.String(255), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    departamento_id = db.Column(db.Integer, db.ForeignKey('departamentos.id'))
    status_aprovacao = db.Column(db.String(50))
    created_at = db.Column(db.TIMESTAMP, default=lambda: datetime.now(pytz.timezone('America/Manaus')))
    departamento_destino = db.Column(db.Integer)
    descricao = db.Column(db.Text)
    revisor = db.Column(db.Integer)
    nome_revisor = db.Column(db.String)

class Tabelas(db.Model):
    __tablename__ = 'tabelas'
    id_tabela = db.Column(db.Integer, primary_key=True)
    nome_subtabela = db.Column(db.String(255), nullable=False)
    departamento_id = db.Column(db.Integer, db.ForeignKey('departamentos.id'))
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)
    revisor = db.Column(db.Integer)
    nome_revisor = db.Column(db.String)

def create_app():
    with app.app_context():
        try:
            db.create_all()
            print("Tabela criada com sucesso!")
        except Exception as e:
            print(f"Erro ao criar tabela: {str(e)}")

# Chamando a função create_app
create_app()