from flask import Blueprint, request, jsonify
from src.services.alert_service import AlertService
from src.adapters.repository import EmpresaRepository

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/controlador/<string:controlador_id>/alerts', methods=['GET'])
def get_controller_alerts(controlador_id):
    session = request.environ.get('session')
    service = AlertService(
        empresa_repo=EmpresaRepository(session),
        session=session
    )
    
    alerts = service.get_controller_alerts(controlador_id)
    return jsonify({"alerts": alerts})

@alerts_bp.route('/controlador/<string:controlador_id>/alert-logs', methods=['GET'])
def get_controller_alert_logs(controlador_id):
    session = request.environ.get('session')
    service = AlertService(
        empresa_repo=EmpresaRepository(session),
        session=session
    )
    
    logs = service.get_controller_alert_logs(controlador_id)
    return jsonify({"logs": logs}) 