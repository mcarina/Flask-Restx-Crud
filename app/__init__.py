from flask import Flask
from flask_cors import CORS
from .extensions import api, db, jwt
from .apis import ns, authorizations
from dotenv import load_dotenv
import os

from datetime import timedelta
import urllib.parse

load_dotenv()
uri_modificada = os.getenv('URI')

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = uri_modificada
    app.config["JWT_SECRET_KEY"] = "senha"
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(hours=5)

    api.init_app(app, authorizations=authorizations)
    db.init_app(app)
    jwt.init_app(app)

    # CORS(app, resources={r"/api/*": {"origins": ["http://127.0.0.1:3000", "http://172.16.17.51:3000"]}})    
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    api.add_namespace(ns)

    return app