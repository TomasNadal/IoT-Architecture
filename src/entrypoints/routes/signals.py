from flask import Blueprint, request, jsonify
from src.services.signal_service import SignalService
from src.adapters.repository import EmpresaRepository
from src.queries.queries import SignalQueries
from datetime import datetime
from src.entrypoints.auth import require_permissions

signals_bp = Blueprint('signals', __name__)

@signals_bp.route('', methods=['POST'])
def create_signal():
    try:
        session = request.environ.get('session')
        service = SignalService(
            empresa_repo=EmpresaRepository(session),
            session=session
        )
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        result = service.process_incoming_signal(data)
        return jsonify(result), 201
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Error processing signal: {str(e)}")
        return jsonify({"error": str(e)}), 500

# No auth decorator for input endpoint
@signals_bp.route("/input", methods=["POST"])
def receive_signal():
    session = request.environ.get('session')
    try:
        data = request.get_json()
        if not data or 'controlador_id' not in data or 'sensor_states' not in data:
            return jsonify({"error": "Missing required fields"}), 400

        service = SignalService(
            empresa_repo=EmpresaRepository(session),
            session=session
        )
        
        signal_data = {
            "tstamp": datetime.now().isoformat(),
            "values": data['sensor_states'],
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "metadata": data.get("metadata", {}),
            "controlador_id": data['controlador_id']
        }
        
        result = service.process_incoming_signal(signal_data)
        return jsonify(result), 201
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Error receiving signal: {str(e)}")
        return jsonify({"error": str(e)}), 500

# All other endpoints require authentication
@signals_bp.route("/<int:controlador_id>", methods=["GET"])
@require_permissions(['view_signals'])
def get_signals(controlador_id):
    session = request.environ.get('session')
    try:
        start_time = request.args.get('start_time', type=datetime.fromisoformat)
        end_time = request.args.get('end_time', type=datetime.fromisoformat)
        user_id = request.args.get('user_id', type=int)
        
        if not all([start_time, end_time, user_id]):
            return jsonify({"error": "Missing required parameters"}), 400

        service = SignalService(
            empresa_repo=EmpresaRepository(session),
            signal_queries=SignalQueries(session)
        )
        
        signals = service.get_controlador_signals(
            user_id=user_id,
            controlador_id=controlador_id,
            start_time=start_time,
            end_time=end_time
        )
        
        return jsonify([s.to_dict() for s in signals]), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400 