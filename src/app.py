from flask import Flask
from flask_cors import CORS
from src.config import Config
from src.entrypoints.middleware import setup_middleware
from src.services.auth_service import AuthService
from src.adapters.repository import UserRepository
from src.entrypoints.routes import auth_bp, empresas_bp, users_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    CORS(app)
    
    # Setup auth service
    user_repo = UserRepository(app.session)
    auth_service = AuthService(user_repo, app.config['JWT_SECRET_KEY'])
    
    # Setup middleware
    setup_middleware(app, auth_service)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(empresas_bp, url_prefix='/api/empresas')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    
    return app 