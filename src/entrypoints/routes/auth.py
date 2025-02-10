from flask import Blueprint, request, jsonify, g, current_app
from src.services.auth_service import AuthService
from functools import wraps
import jwt
from src.services.empresa_service import EmpresaService
from src.adapters.repository import EmpresaRepository
from src.queries.queries import SignalQueries
from src.domain.model import Role

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        session = request.environ['session']
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"error": "Missing email or password"}), 400
            
        auth_service = AuthService(session)
        token = auth_service.authenticate(data['email'], data['password'])
        
        if token:
            return jsonify({"token": token}), 200
        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({"error": str(e)}), 500

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

@auth_bp.route('/me', methods=['GET'])
@require_permissions(['view_dashboard'])
def get_user_info():
    user = g.current_user
    session = request.environ['session']
    
    # Base user info
    user_info = {
        "user": {
            "email": user.email,
            "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
            "permissions": list(user.permissions)
        }
    }
    
    # Check if role is admin (handle both Enum and string cases)
    is_admin = (
        (hasattr(user.role, 'value') and user.role == Role.ADMIN) or
        (isinstance(user.role, str) and user.role.lower() == 'admin')
    )
    
    if is_admin:
        service = EmpresaService(
            empresa_repo=EmpresaRepository(session),
            signal_queries=SignalQueries(session),
            session=session
        )
        empresas = service.get_empresas()
        user_info.update({
            "isAdmin": True,
            "empresas": empresas
        })
    else:
        service = EmpresaService(
            empresa_repo=EmpresaRepository(session),
            signal_queries=SignalQueries(session),
            session=session
        )
        empresa = service.get_empresa(user.empresa.id) if user.empresa else None
        user_info.update({
            "isAdmin": False,
            "empresa": empresa
        })
    
    return jsonify(user_info)

@auth_bp.route('/set-current-empresa/<string:empresa_id>', methods=['POST'])
@require_permissions(['admin'])
def set_current_empresa(empresa_id):
    user = g.current_user
    if user.role != 'ADMIN':
        return jsonify({"error": "Only admins can change empresas"}), 403
        
    session = request.environ['session']
    empresa_repo = EmpresaRepository(session)
    empresa = empresa_repo.get(empresa_id)
    
    if not empresa:
        return jsonify({"error": "Empresa not found"}), 404
        
    # Store current empresa in session
    session['current_empresa_id'] = empresa_id
    
    return jsonify({
        "message": "Current empresa set successfully",
        "empresa": {
            "id": empresa.id,
            "name": empresa.name
        }
    }) 