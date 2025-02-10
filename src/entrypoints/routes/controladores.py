from flask import Blueprint, current_app, request, jsonify, g
from datetime import datetime, timedelta
from src.services.controller_monitoring_service import ControllerMonitoringService
from src.services.controller_analytics_service import ControllerAnalyticsService
from src.services.controller_configuration_service import ControllerConfigurationService
from src.adapters.repository import EmpresaRepository
from src.queries.queries import SignalQueries
from src.entrypoints.auth import require_permissions

controladores_bp = Blueprint('controladores', __name__)

@controladores_bp.route('/<string:controlador_id>/config', methods=['GET', 'POST'])
@require_permissions(['manage_controller'])
def controller_config(controlador_id):
    session = request.environ.get('session')
    service = ControllerConfigurationService(
        empresa_repo=EmpresaRepository(session),
        signal_queries=SignalQueries(session),
        session=session
    )
    
    if request.method == 'GET':
        return jsonify(service.get_config(controlador_id))
    
    new_config = request.get_json()
    return jsonify(service.update_config(controlador_id, new_config))

@controladores_bp.route('', methods=['POST'])
@require_permissions(['manage_controller'])
def create_controller():
    try:
        session = request.environ.get('session')
        user = g.current_user
        service = ControllerConfigurationService(
            empresa_repo=EmpresaRepository(session),
            signal_queries=SignalQueries(session),
            session=session
        )
        
        data = request.get_json()
        if not data or 'empresa_id' not in data:
            return jsonify({"error": "empresa_id is required"}), 400
            
        empresa_id = int(data.pop('empresa_id'))
        if not user.can_access_empresa(empresa_id):
            return jsonify({"error": "Unauthorized access to empresa"}), 403
            
        # Model validation will handle the rest
        controller = service.create_controller(empresa_id, data)
        return jsonify(controller), 201
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Error creating controller: {str(e)}")
        return jsonify({"error": str(e)}), 500

@controladores_bp.route('/<string:controlador_id>/sensor/<string:sensor_id>/connection-data')
@require_permissions(['view_signals'])
def get_connection_data(controlador_id, sensor_id):
    session = request.environ.get('session')
    user = g.current_user
    service = ControllerAnalyticsService(
        empresa_repo=EmpresaRepository(session),
        signal_queries=SignalQueries(session)
    )
    
    start_date = datetime.fromisoformat(request.args.get('startDate'))
    end_date = datetime.fromisoformat(request.args.get('endDate'))
    
    return jsonify(service.get_sensor_connection_data(
        controlador_id, sensor_id, start_date, end_date, user.permissions
    ))

@controladores_bp.route('/<string:controlador_id>/changes')
def get_controller_changes(controlador_id):
    session = request.environ.get('session')
    service = ControllerAnalyticsService(
        empresa_repo=EmpresaRepository(session),
        signal_queries=SignalQueries(session)
    )
    return jsonify(service.get_sensor_changes(controlador_id))

@controladores_bp.route('/<string:controlador_id>/sensor_activity')
@require_permissions(['view_signals'])
def get_sensor_activity(controlador_id):
    session = request.environ.get('session')
    user = g.current_user
    service = ControllerAnalyticsService(
        empresa_repo=EmpresaRepository(session),
        signal_queries=SignalQueries(session)
    )
    return jsonify(service.get_sensor_activity(controlador_id, user.permissions))

@controladores_bp.route('/<string:controlador_id>/sensor_uptime')
@require_permissions(['view_signals'])
def get_sensor_uptime(controlador_id):
    session = request.environ.get('session')
    user = g.current_user
    service = ControllerAnalyticsService(
        empresa_repo=EmpresaRepository(session),
        signal_queries=SignalQueries(session)
    )
    return jsonify(service.get_sensor_uptime(controlador_id, user.permissions))

@controladores_bp.route('/<string:controlador_id>/sensor_correlation')
def get_sensor_correlation(controlador_id):
    session = request.environ.get('session')
    service = ControllerAnalyticsService(
        empresa_repo=EmpresaRepository(session),
        signal_queries=SignalQueries(session)
    )
    return jsonify(service.get_sensor_correlation(controlador_id))

@controladores_bp.route('/<string:controlador_id>/alerts')
def get_controller_alerts(controlador_id):
    session = request.environ.get('session')
    service = ControllerMonitoringService(
        empresa_repo=EmpresaRepository(session),
        signal_queries=SignalQueries(session)
    )
    return jsonify(service.get_controller_alerts(controlador_id))

@controladores_bp.route('/<string:controlador_id>/uptime-downtime')
def get_uptime_downtime(controlador_id):
    session = request.environ.get('session')
    service = ControllerAnalyticsService(
        empresa_repo=EmpresaRepository(session),
        signal_queries=SignalQueries(session)
    )
    
    start_date = datetime.fromisoformat(request.args.get('start_date'))
    end_date = datetime.fromisoformat(request.args.get('end_date'))
    
    return jsonify(service.get_uptime_downtime(controlador_id, start_date, end_date))

@controladores_bp.route('/<string:controlador_id>/operational-hours')
def get_operational_hours(controlador_id):
    session = request.environ.get('session')
    service = ControllerAnalyticsService(
        empresa_repo=EmpresaRepository(session),
        signal_queries=SignalQueries(session)
    )
    
    start_date = datetime.fromisoformat(request.args.get('start_date'))
    end_date = datetime.fromisoformat(request.args.get('end_date'))
    
    return jsonify(service.get_operational_hours(controlador_id, start_date, end_date))

@controladores_bp.route('/<string:controlador_id>/timeline')
def get_controller_timeline(controlador_id):
    session = request.environ.get('session')
    service = ControllerAnalyticsService(
        empresa_repo=EmpresaRepository(session),
        signal_queries=SignalQueries(session)
    )
    
    start_date = datetime.fromisoformat(request.args.get('start_date'))
    end_date = datetime.fromisoformat(request.args.get('end_date'))
    
    return jsonify(service.get_timeline_data(controlador_id, start_date, end_date))

@controladores_bp.route('/<string:controlador_id>', methods=['DELETE'])
def delete_controller(controlador_id):
    session = request.environ.get('session')
    service = ControllerConfigurationService(
        empresa_repo=EmpresaRepository(session),
        signal_queries=SignalQueries(session)
    )
    
    service.delete_controller(controlador_id)
    return '', 204 