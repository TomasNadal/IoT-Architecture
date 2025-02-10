from flask import Blueprint, request, jsonify, g
from src.entrypoints.auth import require_permissions

users_bp = Blueprint('users', __name__)

@users_bp.route("", methods=["GET"])
@require_permissions(['manage_users'])
def list_users():
    session = request.environ['session']
    user = g.current_user
    service = UserService(session)
    return jsonify(service.list_users(user.permissions))

@users_bp.route("/<int:user_id>", methods=["GET"])
@require_permissions(['manage_users'])
def get_user(user_id):
    session = request.environ['session']
    user = g.current_user
    service = UserService(session)
    return jsonify(service.get_user(user_id, user.permissions))

empresas_bp = Blueprint('empresas', __name__)

@empresas_bp.route("", methods=["GET"])
def list_empresas():
    # Implementation
    pass

@empresas_bp.route("/<int:empresa_id>", methods=["GET"])
def get_empresa(empresa_id):
    # Implementation
    pass 