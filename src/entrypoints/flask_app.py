from flask import Flask, request
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from ..config import (
    get_postgres_uri, 
    get_jwt_secret, 
    get_app_secret,
    get_cors_origins
)
from .routes.signals import signals_bp
from .routes.users import users_bp
from .routes.empresas import empresas_bp
from .routes.dashboard import dashboard_bp
from .routes.controladores import controladores_bp
from .routes.auth import auth_bp
from ..services.auth_service import AuthService
from .middleware import setup_middleware
from flask_cors import CORS
from src.bootstrap import create_initial_data

# Create Flask app
app = Flask(__name__)
app.secret_key = get_app_secret()
CORS(app)

# Database setup
engine = create_engine(get_postgres_uri())
get_session = sessionmaker(bind=engine)

# Setup auth service with session
auth_service = AuthService(get_session(), get_jwt_secret())

# Setup middleware
setup_middleware(app, auth_service)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(empresas_bp, url_prefix='/api/empresas')
app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(signals_bp, url_prefix='/api/signals')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
app.register_blueprint(controladores_bp, url_prefix='/api/controladores')

# Middleware to inject database session
@app.before_request
def inject_session():
    session = get_session()
    request.environ['session'] = session

@app.teardown_request
def remove_session(exception=None):
    session = request.environ.pop('session', None)
    if session:
        session.close()

def create_app(session_factory):
    app = Flask(__name__)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(signals_bp, url_prefix='/api/signals')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(controladores_bp, url_prefix='/api/controladores')
    app.register_blueprint(empresas_bp, url_prefix='/api/empresas')
    
    # Create a session for initialization
    session = session_factory()
    create_initial_data(session)
    session.close()
    
    return app

if __name__ == '__main__':
    app.run(debug=True)
