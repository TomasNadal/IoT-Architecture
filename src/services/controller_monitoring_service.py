from datetime import datetime, timedelta
from typing import Dict, List, Optional
import src.domain.model as m
from src.adapters.repository import EmpresaRepository
from src.queries.queries import SignalQueries

class ControllerMonitoringService:
    def __init__(
        self,
        empresa_repo: EmpresaRepository,
        signal_queries: SignalQueries
    ):
        self.empresa_repo = empresa_repo
        self.signal_queries = signal_queries

    def get_controller_status(self, controller_id: str, user_permissions: List[str]) -> Dict:
        """Get current status of a controller"""
        if 'view_signals' not in user_permissions:
            raise ValueError("Insufficient permissions")
        
        latest_signal = self.signal_queries.get_latest_by_controller(
            controller_id, 
            1,
            user_permissions
        )
        controller = self.empresa_repo.get_by_id(controller_id)
        
        if not latest_signal:
            return {"status": "offline", "last_seen": None}

        is_connected = self._check_connection_status(latest_signal[0].tstamp)
        
        return {
            "status": "online" if is_connected else "offline",
            "last_seen": latest_signal[0].tstamp.isoformat(),
            "controller_name": controller.name
        }

    def get_empresa_dashboard(self, empresa_id: str, user_permissions: List[str]) -> List[Dict]:
        """Get dashboard data for all controllers in a company"""
        if 'view_dashboard' not in user_permissions:
            raise ValueError("Insufficient permissions")
        
        controllers = self.empresa_repo.get_by_empresa(empresa_id)
        
        dashboard_data = []
        for controller in controllers:
            latest_signals = self.signal_queries.get_latest_by_controller(
                controller.id, 
                10,
                user_permissions
            )
            
            # Use to_dict() instead of to_frontend_format()
            formatted_signals = [signal.to_dict() for signal in latest_signals]
            
            controller_data = {
                "id": str(controller.id),
                "name": controller.name,
                "signals": formatted_signals,
                "config": controller.config
            }
            
            dashboard_data.append(controller_data)

        return dashboard_data

    def get_empresa_connected_stats(self, empresa_id: str, user_permissions: List[str]) -> Dict:
        """Get connected/disconnected stats for empresa"""
        if 'view_dashboard' not in user_permissions:
            raise ValueError("Insufficient permissions")
            
        controllers = self.empresa_repo.get_by_empresa(empresa_id)
        connected = 0
        disconnected = 0
        
        for controller in controllers:
            latest_signal = self.signal_queries.get_latest_by_controller(
                controller.id, 1, user_permissions
            )
            if latest_signal and self._check_connection_status(latest_signal[0].tstamp):
                connected += 1
            else:
                disconnected += 1
                
        return {
            "connected": connected,
            "disconnected": disconnected
        }

    @staticmethod
    def _check_connection_status(last_signal_time: datetime, threshold_minutes: int = 5) -> bool:
        return (datetime.now() - last_signal_time) <= timedelta(minutes=threshold_minutes) 