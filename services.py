from datetime import datetime
from typing import Optional
import model as m
from repository import EmpresaRepository
from queries import SignalQueries

class SignalService:
    def __init__(
        self,
        empresa_repo: EmpresaRepository,
        signal_queries: SignalQueries
    ):
        self.empresa_repo = empresa_repo
        self.signal_queries = signal_queries

    def process_incoming_signal(self, signal_dto: m.IncomingSignalDTO) -> m.Signal:
        # Get controlador by phone number
        controlador = self.empresa_repo.get_controlador_by_phone(signal_dto.controlador_id)
        if not controlador:
            raise ValueError(f"Controller not found: {signal_dto.controlador_id}")

        # Create signal from incoming data
        signal = m.Signal(
            tstamp=datetime.now(),
            values=self._process_sensor_values(signal_dto.sensor_values),
            latitude=0.0,  # You might want to add these to DTO
            longitude=0.0, # You might want to add these to DTO
            metadata={"location": signal_dto.location},
            _controlador=controlador
        )

        # Add signal to controlador
        controlador.add_signal(signal)
        
        return signal

    def _process_sensor_values(self, sensor_values: list[int]) -> dict:
        return {
            f"sensor{i+1}": value == 1 
            for i, value in enumerate(sensor_values)
        }