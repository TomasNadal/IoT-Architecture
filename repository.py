from sqlalchemy.orm import Session
from typing import List, Optional
import model as m
from datetime import datetime


class AbstractRepository:
    """Handles write operations and aggregate consistency"""
    def __init__(self, session: Session):
        self.session = session

    def add(self, empresa: m.Empresa):
        pass
    
    def get(self, id) -> Optional[m.Empresa]:
        pass
    
    def commit(self):
        pass

    def list(self):
        raise NotImplementedError

class EmpresaRepository(AbstractRepository):
    """Handles write operations and aggregate consistency"""
    def __init__(self, session: Session):
        self.session = session

    def add(self, empresa: m.Empresa):
        self.session.add(empresa)
    
    def get(self, id) -> Optional[m.Empresa]:
        return self.session.query(m.Empresa).filter_by(id=id).first()
    
    def commit(self):
        self.session.commit()

    def list(self) -> List[m.Empresa]:
        return self.session.query(m.Empresa).all()

    def get_controlador_by_phone(self, phone_number: str) -> Optional[m.Controlador]:
        return self.session.query(m.Controlador)\
            .filter_by(phone_number=phone_number)\
            .first()
