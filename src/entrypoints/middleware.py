from functools import wraps
from flask import request, jsonify, g, current_app, make_response
from flask_cors import CORS
from src.services.auth_service import AuthService
from src.services.auth import UserPermissions
from src.config import get_cors_origins

def setup_middleware(app, auth_service: AuthService):
    # Setup CORS with specific origins
    CORS(app, 
         resources={
             r"/api/*": {
                 "origins": ["http://localhost:5174", "http://127.0.0.1:5174"],
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                 "allow_headers": ["Authorization", "Content-Type"],
                 "expose_headers": ["Content-Type"],
                 "supports_credentials": True,
                 "max_age": 600
             }
         })
    
    @app.before_request
    def verify_token():
        # Skip for OPTIONS and public endpoints
        if (request.method == 'OPTIONS' or
            request.endpoint == 'auth.login' or
            request.endpoint == 'signals.receive_signal' or
            'socket.io' in request.path):
            return
            
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "No token provided"}), 401
            
        try:
            token = auth_header.split(' ')[1]
            payload = auth_service.verify_token(token)
            
            if not payload:
                return jsonify({"error": "Invalid token"}), 401
                
            # Store user in g for the request duration
            g.current_user = UserPermissions(
                user_id=payload['user_id'],
                email=payload['email'],
                role=payload['role'],
                permissions=set(payload['permissions'])
            )
            
        except Exception as e:
            return jsonify({"error": f"Token verification failed: {str(e)}"}), 401

    # Add OPTIONS handling for all routes
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = make_response()
            response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            response.headers.add('Access-Control-Allow-Headers', 'Authorization, Content-Type')
            return response, 200 