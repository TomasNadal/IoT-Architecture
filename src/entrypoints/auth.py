from functools import wraps
from flask import request, jsonify, g, Blueprint, current_app
from typing import List, Optional, Dict
from src.config import get_jwt_secret
from src.services.auth_service import AuthService
import jwt
from src.services.empresa_service import EmpresaService
from src.adapters.repository import EmpresaRepository
from src.queries.queries import SignalQueries
from src.domain.model import Role

PUBLIC_ENDPOINTS = [
    '/api/signals/input'  # Allow controller signals without auth
]

def require_token():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Skip auth for public endpoints
            if request.path in PUBLIC_ENDPOINTS:
                return f(*args, **kwargs)

            # Check token for protected endpoints    
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({"error": "No token provided"}), 401
                
            try:
                # Rest of your existing token validation logic
                token = token.split(' ')[1]  # Remove 'Bearer ' prefix
                payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
                g.current_user = payload
                return f(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token has expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401
                
        return decorated_function
    return decorator

def require_permissions(permissions):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Get token from header
                auth_header = request.headers.get('Authorization')
                if not auth_header:
                    return jsonify({"error": "No token provided"}), 401
                
                # Extract token from "Bearer <token>"
                token = auth_header.split(' ')[1] if len(auth_header.split(' ')) > 1 else auth_header
                
                # Verify token
                session = request.environ['session']
                auth_service = AuthService(session)
                payload = auth_service.verify_token(token)
                
                if not payload:
                    return jsonify({"error": "Invalid token"}), 401
                
                # Check if user has required permissions
                user_permissions = set(payload.get('permissions', []))
                if not all(p in user_permissions for p in permissions):
                    return jsonify({"error": "Insufficient permissions"}), 403
                
                # Store user info in flask.g
                g.current_user = auth_service.get_user_by_email(payload['email'])
                
                return f(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token has expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401
            except Exception as e:
                print(f"Auth error: {str(e)}")
                return jsonify({"error": str(e)}), 500
        return decorated_function
    return decorator

def verify_token(token: str) -> Dict:
    try:
        auth_service = AuthService(session)
        return auth_service.verify_token(token)
    except Exception as e:
        raise ValueError(f"Token verification failed: {str(e)}") 