from sqlalchemy.orm import Session
from typing import List, Optional, Dict
import src.domain.model as m
from datetime import datetime


class EmpresaRepository:
    def __init__(self, session: Session):
        self.session = session

    # Empresa access methods
    def add(self, empresa: m.Empresa) -> None:
        """Add new empresa"""
        self.session.add(empresa)
    
    def get(self, empresa_id: int) -> Optional[m.Empresa]:
        """Get empresa by ID"""
        return self.session.query(m.Empresa).filter(m.Empresa.id == empresa_id).first()
    
    def get_all(self) -> List[m.Empresa]:
        """Get all empresas"""
        return self.session.query(m.Empresa).all()

    def get_by_empresa(self, empresa_id: int) -> List[m.Controlador]:
        """Get all controllers for an empresa"""
        empresa = self.get(empresa_id)
        if not empresa:
            return []
        return empresa.controladores

    def get_by_id(self, id: int) -> Optional[m.Empresa]:
        """Get empresa by ID (alias for get)"""
        return self.get(id)

    # Controlador access methods
    def get_controlador(self, controlador_id: int) -> Optional[m.Controlador]:
        """Get controller by ID"""
        return self.session.query(m.Controlador).get(controlador_id)
    
    def get_controlador_by_phone(self, phone_number: str) -> Optional[m.Controlador]:
        """Get controller by phone number"""
        return self.session.query(m.Controlador).filter(
            m.Controlador.phone_number == phone_number
        ).first()
    
    def get_controlador_by_id(self, controlador_id: str) -> Optional[m.Controlador]:
        return (self.session.query(m.Controlador)
                .join(m.Empresa)
                .filter(m.Controlador.id == controlador_id)
                .first())
    
    def get_controladores_by_empresa(self, empresa_id: int) -> List[m.Controlador]:
        return (self.session.query(m.Controlador)
                .join(m.Empresa)
                .filter(m.Empresa.id == empresa_id)
                .all())