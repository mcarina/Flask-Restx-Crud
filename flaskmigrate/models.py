from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from dotenv import load_dotenv
import os


load_dotenv()
app = Flask(__name__)
# uri_modificada = os.getenv('URI')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('URI')
db = SQLAlchemy(app)

class Usuarios(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.Text)
    
    def to_dict(self):
        return {
            "email": self.email,
            "nome": self.nome,
            # Adicione outros campos se necessário
        }    

def create_app():
    with app.app_context():
        try:
            db.create_all()
            print("Tabela criada com sucesso!")
        except Exception as e:
            print(f"Erro ao criar tabela: {str(e)}")

# Chamando a função create_app
create_app()