from flask import Flask, request, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import config
import model as m
from repository import EmpresaRepository
from queries import SignalQueries, PermissionQueries
from services import SignalService
from datetime import datetime

app = Flask(__name__)

# Database setup
engine = create_engine(config.get_postgres_uri())
get_session = sessionmaker(bind=engine)

@app.route("/api/signals/<int:controlador_id>", methods=["GET"])
def get_signals(controlador_id):
    session = get_session()
    try:
        # Get query parameters
        start_time = request.args.get('start_time', type=datetime.fromisoformat)
        end_time = request.args.get('end_time', type=datetime.fromisoformat)
        user_id = request.args.get('user_id', type=int)
        
        if not all([start_time, end_time, user_id]):
            return jsonify({"error": "Missing required parameters"}), 400

        # Initialize service with repositories
        service = SignalService(
            empresa_repo=EmpresaRepository(session),
            signal_queries=SignalQueries(session),
            permission_queries=PermissionQueries(session)
        )
        
        # Service handles all business logic
        signals = service.get_controlador_signals(
            user_id=user_id,
            controlador_id=controlador_id,
            start_time=start_time,
            end_time=end_time
        )
        
        # Transform to JSON response
        return jsonify([{
            "tstamp": s.tstamp.isoformat(),
            "values": s.values,
            "latitude": s.latitude,
            "longitude": s.longitude,
            "metadata": s.metadata
        } for s in signals]), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()

@app.route("/api/dashboard/<int:empresa_id>", methods=["GET"])
def get_dashboard(empresa_id):
    session = get_session()
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({"error": "Missing user_id parameter"}), 400

        service = SignalService(
            empresa_repo=EmpresaRepository(session),
            signal_queries=SignalQueries(session),
            permission_queries=PermissionQueries(session)
        )
        
        summaries = service.get_controlador_dashboard(
            user_id=user_id,
            empresa_id=empresa_id
        )
        
        return jsonify([{
            "controlador_id": s.controlador_id,
            "controlador_name": s.controlador_name,
            "last_signal_time": s.last_signal_time.isoformat() if s.last_signal_time else None,
            "signal_count": s.signal_count,
            "latest_values": s.latest_values
        } for s in summaries]), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()

@app.route("/api/signals", methods=["POST"])
def receive_signal():
    session = get_session()
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 415
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON format"}), 400

        # Use your DTO to validate/parse incoming data
        try:
            signal_dto = m.IncomingSignalDTO.from_json(data)
        except (KeyError, ValueError) as e:
            return jsonify({"error": f"Invalid data format: {str(e)}"}), 400

        # Process signal
        service = SignalService(
            empresa_repo=EmpresaRepository(session),
            signal_queries=SignalQueries(session)
        )
        
        signal = service.process_incoming_signal(signal_dto)
        session.commit()
        
        return jsonify({
            "status": "success",
            "signal_id": signal.id,
            "timestamp": signal.tstamp.isoformat()
        }), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        session.rollback()
        return jsonify({"error": "Internal server error"}), 500
    finally:
        session.close()
