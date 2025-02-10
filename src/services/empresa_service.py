from typing import Dict, List, Optional
from datetime import datetime
from src.domain import model as m
from src.adapters.repository import EmpresaRepository
from src.queries.queries import SignalQueries
from sqlalchemy.orm import Session
from src.domain.model import Empresa

class EmpresaService:
    def __init__(
        self,
        empresa_repo: EmpresaRepository,
        signal_queries: SignalQueries,
        session: Session
    ):
        self.empresa_repo = empresa_repo
        self.signal_queries = signal_queries
        self.session = session

    def get_empresas(self) -> List[Dict]:
        """Get all empresas"""
        empresas = self.session.query(Empresa).all()
        return [
            {
                'id': e.id,
                'name': e.name,
                'phone_number': e.phone_number,
                'email': e.email
            }
            for e in empresas
        ]

    def create_empresa(self, data: dict) -> dict:
        """Create a new empresa"""
        empresa = Empresa(
            name=data['name'],
            phone_number=data['phone_number'],
            email=data['email']
        )
        
        self.session.add(empresa)
        self.session.commit()
        
        return {
            'id': empresa.id,
            'name': empresa.name,
            'phone_number': empresa.phone_number,
            'email': empresa.email
        }

    def update_empresa(self, empresa_id: int, data: Dict, user_permissions: List[str]) -> Dict:
        """Update existing empresa"""
        if 'manage_empresa' not in user_permissions:
            raise ValueError("Insufficient permissions")
            
        empresa = self.empresa_repo.get(empresa_id)
        if not empresa:
            raise ValueError(f"Empresa not found: {empresa_id}")
            
        # Update fields
        if 'name' in data:
            empresa.name = data['name']
        if 'phone_number' in data:
            empresa._validate_phone(data['phone_number'])
            empresa.phone_number = data['phone_number']
        if 'email' in data:
            empresa._validate_email(data['email'])
            empresa.email = data['email']
            
        return empresa.to_dict()

    def get_empresa(self, empresa_id: int) -> dict:
        """Get empresa by id"""
        empresa = self.session.query(Empresa).get(empresa_id)
        if not empresa:
            return None
            
        return {
            'id': empresa.id,
            'name': empresa.name,
            'phone_number': empresa.phone_number,
            'email': empresa.email
        }

    def delete_empresa(self, empresa_id: int, user_permissions: List[str]) -> None:
        """Delete empresa"""
        if 'manage_empresa' not in user_permissions:
            raise ValueError("Insufficient permissions")
            
        empresa = self.empresa_repo.get(empresa_id)
        if not empresa:
            raise ValueError(f"Empresa not found: {empresa_id}")
            
        self.empresa_repo.delete(empresa)

    def get_user_empresa(self, user_id: int) -> Optional[Empresa]:
        """Get the empresa assigned to a user"""
        user = self.session.query(m.User).get(user_id)
        if not user:
            return None
        return user.empresa 

    def get_empresas_stats(self) -> Dict[str, Dict]:
        """Get stats for all empresas"""
        empresas = self.session.query(Empresa).all()
        stats = {}
        
        for empresa in empresas:
            # Count users associated with this empresa
            user_count = self.session.query(m.User)\
                .filter(m.User.empresa_id == empresa.id)\
                .count()
            
            # Count controllers associated with this empresa
            controller_count = self.session.query(m.Controlador)\
                .filter(m.Controlador.empresa_id == empresa.id)\
                .count()
            
            stats[str(empresa.id)] = {
                "users": user_count,
                "controllers": controller_count
            }
        
        return stats 