from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from src.domain.model import Controlador, Empresa
from src.adapters.repository import EmpresaRepository
from src.queries.queries import SignalQueries

class ControllerConfigurationService:
    def __init__(
        self,
        empresa_repo: EmpresaRepository,
        signal_queries: SignalQueries,
        session: Session
    ):
        self.empresa_repo = empresa_repo
        self.signal_queries = signal_queries
        self.session = session

    def get_controller_config(self, controller_id: int, user_permissions: list) -> Optional[Dict]:
        """Get controller configuration"""
        if 'view_controller_config' not in user_permissions:
            raise ValueError("Insufficient permissions")
            
        controller = self.session.query(Controlador).get(controller_id)
        if not controller:
            return None
            
        return controller.config

    def update_controller_config(self, controller_id: int, config: Dict, user_permissions: list) -> bool:
        """Update controller configuration"""
        if 'manage_controller_config' not in user_permissions:
            raise ValueError("Insufficient permissions")
            
        controller = self.session.query(Controlador).get(controller_id)
        if not controller:
            return False
            
        controller.config = config
        self.session.commit()
        return True

    def create_controller(self, empresa_id: int, data: Dict) -> Dict:
        """Create a new controller with the given configuration"""
        try:
            empresa = self.empresa_repo.get(empresa_id)
            if not empresa:
                raise ValueError(f"Empresa not found with ID: {empresa_id}")
            
            # Validate required fields
            required_fields = ['name', 'phone_number']
            if not all(field in data for field in required_fields):
                raise ValueError(f"Missing required fields: {required_fields}")
            
            controller = Controlador(
                name=data['name'],
                phone_number=data['phone_number'],
                config=data.get('config', {})
            )
            
            empresa.add_controlador(controller)
            self.session.commit()
            
            return {
                'id': controller.id,
                'empresa_id': empresa.id,
                'name': controller.name,
                'phone_number': controller.phone_number,
                'config': controller.config
            }
            
        except Exception as e:
            self.session.rollback()
            print(f"Error in create_controller: {str(e)}")
            raise

    def delete_controller(self, controller_id: int) -> None:
        """Delete a controller"""
        controller = self.session.query(Controlador).get(controller_id)
        if not controller:
            return
            
        self.session.delete(controller)
        self.session.commit()

    @staticmethod
    def _validate_config(config: Dict) -> None:
        """Validate controller configuration"""
        required_fields = ['sensor_types', 'thresholds', 'sampling_rate']
        if not all(field in config for field in required_fields):
            raise ValueError("Invalid configuration: missing required fields") 