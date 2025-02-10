from flask import Blueprint, current_app, request, jsonify, g
from datetime import datetime, timedelta
from src.services.controller_monitoring_service import ControllerMonitoringService
from src.services.controller_analytics_service import ControllerAnalyticsService
from src.services.controller_configuration_service import ControllerConfigurationService
from src.adapters.repository import EmpresaRepository
from src.queries.queries import SignalQueries
from src.entrypoints.auth import require_permissions

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/empresa/<string:empresa_id>/dashboard')
@require_permissions(['view_dashboard'])
def get_empresa_dashboard(empresa_id):
    session = request.environ.get('session')
    user = g.current_user
    service = ControllerMonitoringService(
        empresa_repo=EmpresaRepository(session),
        signal_queries=SignalQueries(session)
    )
    return jsonify(service.get_empresa_dashboard(empresa_id, user.permissions))

@dashboard_bp.route('/controlador/<string:controlador_id>/detail')
@require_permissions(['view_signals'])
def get_controller_detail(controlador_id):
    session = request.environ.get('session')
    user = g.current_user
    service = ControllerMonitoringService(
        empresa_repo=EmpresaRepository(session),
        signal_queries=SignalQueries(session)
    )
    return jsonify(service.get_controller_status(controlador_id, user.permissions))

@dashboard_bp.route('/controlador/<string:controlador_id>/analytics')
def get_controller_analytics(controlador_id):
    session = request.environ.get('session')
    service = ControllerAnalyticsService(
        empresa_repo=EmpresaRepository(session),
        signal_queries=SignalQueries(session)
    )
    days = request.args.get('days', 7, type=int)
    return jsonify(service.get_sensor_correlation(controlador_id, hours=days*24))

@dashboard_bp.route('/controlador/<string:controlador_id>/config', methods=['GET', 'POST'])
@require_permissions(['manage_controller'])
def controller_config(controlador_id):
    session = request.environ.get('session')
    user = g.current_user
    service = ControllerConfigurationService(
        empresa_repo=EmpresaRepository(session),
        signal_queries=SignalQueries(session)
    )
    
    if request.method == 'GET':
        return jsonify(service.get_config(controlador_id))
    
    new_config = request.get_json()
    return jsonify(service.update_config(controlador_id, new_config))

