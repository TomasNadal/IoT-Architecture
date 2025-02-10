from flask import Blueprint, request, jsonify, g
from src.services.controller_monitoring_service import ControllerMonitoringService
from src.services.empresa_service import EmpresaService
from src.adapters.repository import EmpresaRepository
from src.queries.queries import SignalQueries
from src.entrypoints.auth import require_permissions

empresas_bp = Blueprint('empresas', __name__)

@empresas_bp.route('', methods=['GET'])
@require_permissions(['view_empresas'])
def get_empresas():
    session = request.environ['session']
    user = g.current_user
    service = EmpresaService(
        empresa_repo=EmpresaRepository(session),
        signal_queries=SignalQueries(session),
        session=session
    )
    return jsonify(service.get_empresas())

@empresas_bp.route('/', methods=['POST'])
@require_permissions(['manage_empresa'])
def create_empresa():
    try:
        session = request.environ['session']
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        service = EmpresaService(
            empresa_repo=EmpresaRepository(session),
            signal_queries=SignalQueries(session),
            session=session
        )
        result = service.create_empresa(data)
        
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@empresas_bp.route('/', methods=['GET'])
@require_permissions(['view_empresas'])
def list_empresas():
    try:
        session = request.environ['session']
        service = EmpresaService(session)
        empresas = service.get_empresas()
        return jsonify(empresas), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@empresas_bp.route('/<int:empresa_id>', methods=['GET'])
@require_permissions(['view_empresas'])
def get_empresa(empresa_id):
    try:
        session = request.environ['session']
        service = EmpresaService(session)
        empresa = service.get_empresa(empresa_id)
        if not empresa:
            return jsonify({"error": "Empresa not found"}), 404
        return jsonify(empresa), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@empresas_bp.route('/<int:empresa_id>', methods=['PUT'])
@require_permissions(['manage_empresa'])
def update_empresa(empresa_id):
    session = request.environ['session']
    user = g.current_user
    service = EmpresaService(
        empresa_repo=EmpresaRepository(session),
        signal_queries=SignalQueries(session)
    )
    data = request.get_json()
    return jsonify(service.update_empresa(empresa_id, data, user.permissions))

@empresas_bp.route('/<int:empresa_id>', methods=['DELETE'])
def delete_empresa(empresa_id):
    session = request.environ['session']
    # TODO: Implement delete empresa logic
    return jsonify({"message": f"Delete empresa {empresa_id} endpoint"}), 200


@empresas_bp.route('/<string:empresa_id>/components')
def get_components(empresa_id):
    session = request.environ.get('session')
    service = ControllerMonitoringService(
        empresa_repo=EmpresaRepository(session),
        signal_queries=SignalQueries(session)
    )
    return jsonify(service.get_empresa_components(empresa_id))

@empresas_bp.route('/<string:empresa_id>/dashboard')
@require_permissions(['view_dashboard'])
def get_empresa_dashboard(empresa_id):
    session = request.environ['session']
    user = g.current_user
    
    service = ControllerMonitoringService(
        empresa_repo=EmpresaRepository(session),
        signal_queries=SignalQueries(session)
    )
    
    return jsonify(service.get_empresa_dashboard(
        empresa_id=empresa_id,
        user_permissions=user.permissions
    ))

@empresas_bp.route('/stats', methods=['GET', 'OPTIONS'])
@require_permissions(['manage_empresa'])
def get_empresas_stats():
    # Handle preflight request
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 200
        
    try:
        session = request.environ['session']
        user = g.current_user
        service = EmpresaService(
            empresa_repo=EmpresaRepository(session),
            signal_queries=SignalQueries(session),
            session=session
        )
        return jsonify(service.get_empresas_stats())
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@empresas_bp.route('/<string:id>/connected_stats')
@require_permissions(['view_dashboard'])
def get_connected_stats(id):
    try:
        session = request.environ.get('session')
        user = g.current_user
        service = ControllerMonitoringService(
            empresa_repo=EmpresaRepository(session),
            signal_queries=SignalQueries(session)
        )
        
        stats = service.get_empresa_connected_stats(id, user.permissions)
        return jsonify(stats)
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Error getting connected stats: {str(e)}")
        return jsonify({"error": str(e)}), 500 