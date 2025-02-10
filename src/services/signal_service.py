from datetime import datetime
from typing import Dict, Optional
from src.domain.model import Signal, Controlador
from src.adapters.repository import EmpresaRepository

class SignalService:
    def __init__(
        self,
        empresa_repo: EmpresaRepository,
        session
    ):
        self.empresa_repo = empresa_repo
        self.session = session

    def process_incoming_signal(self, signal_data: Dict) -> Dict:
        """Process incoming signal from controller"""
        phone_number = signal_data['controlador_id']
        controller = self.session.query(Controlador).filter_by(
            phone_number=phone_number
        ).first()
        
        if not controller:
            raise ValueError(f"No controller found with phone number: {phone_number}")
        
        # Transform sensor values format
        transformed_values = {
            f"sensor{i+1}": signal_data['values'][f"value_sensor{i+1}"]
            for i in range(6)
        }
        
        # Create signal record
        signal = Signal(
            tstamp=datetime.fromisoformat(signal_data['tstamp']),
            values=transformed_values,
            latitude=signal_data.get('latitude'),
            longitude=signal_data.get('longitude'),
            metadata=signal_data.get('metadata', {}),
            _controlador=controller
        )
        
        self.session.add(signal)
        self.session.commit()
        
        return signal.to_dict()

    def _process_sensor_values(self, sensor_values: list) -> dict:
        """Convert raw sensor values to structured data"""
        if isinstance(sensor_values, list):
            return {f"sensor{i+1}": value for i, value in enumerate(sensor_values)}
        return sensor_values  # If it's already a dict, return as is 