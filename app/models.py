from .extensions import db
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
import pytz

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