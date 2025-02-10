from flask import Blueprint, request, jsonify
from src.services.controller_configuration_service import ControllerConfigurationService
from src.entrypoints.auth import require_permissions

controllers_bp = Blueprint('controllers', __name__)

@controllers_bp.route('/', methods=['POST'])
@require_permissions(['manage_controller'])
def create_controller():
    try:
        session = request.environ['session']
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        service = ControllerConfigurationService(session)
        result = service.create_controller(data)
        
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500 