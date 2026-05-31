from flask import Flask
from .config import Config #carregar os .env
from .extensions import db, migrate, cors #carregar as extenções
from .routes.health import health_bp

def create_app():

    app = Flask(__name__)

    app.config.from_object(Config) #carregar as config
    db.init_app(app) #conecta o banco ao app
    migrate.init_app(app, db) #conecta o banco ao app
    cors.init_app(app) #conecta o cors ao app
  
    app.register_blueprint(health_bp)

    return app