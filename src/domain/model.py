from __future__ import annotations
from typing import Optional, List, Dict, Any, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
import uuid
from enum import Enum
from werkzeug.security import generate_password_hash, check_password_hash


'''
Business Exceptions
- InvalidPhoneNumber
- InvalidSignal

'''
class InvalidPhoneNumber(Exception):
    pass

class InvalidSignal(Exception):
    pass

class InvalidEmail(Exception):
    pass


@dataclass
class Signal:
    tstamp: datetime = None
    values: Dict[str, Any] = None
    latitude: float = 0.0
    longitude: float = 0.0
    metadata: Dict[str, Any] = None
    controlador_id: Optional[int] = None
    _controlador: Optional[Controlador] = None

    def to_dict(self) -> Dict:
        """Convert signal to frontend format"""
        return {
            "id": self.id,
            "controlador_id": self._controlador.phone_number if self._controlador else None,
            "tstamp": self.tstamp.isoformat(),
            "latitude": self.latitude,
            "longitude": self.longitude,
            "value_sensor1": bool(self.values.get("sensor1", False)),
            "value_sensor2": bool(self.values.get("sensor2", False)),
            "value_sensor3": bool(self.values.get("sensor3", False)),
            "value_sensor4": bool(self.values.get("sensor4", False)),
            "value_sensor5": bool(self.values.get("sensor5", False)),
            "value_sensor6": bool(self.values.get("sensor6", False))
        }



class Controlador:
    def __init__(self, name: str, phone_number: str, config: Dict[str, Any]):
        self.name = name
        self.phone_number = phone_number
        self.config = config
        self.signals = []
        self._empresa: Optional[Empresa] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert controller to dictionary"""
        return {
            'name': self.name,
            'phone_number': self.phone_number,
            'config': self.config,
            'empresa_id': self._empresa.id if self._empresa else None,
            'id': self.id  # SQLAlchemy will provide this
        }

    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update controller configuration"""
        self._validate_config(new_config)
        self.config = new_config

    def add_signal(self, signal: Signal) -> None:
        if not isinstance(signal, Signal):
            raise InvalidSignal
        self.signals.append(signal)
    
    def set_empresa(self, empresa: Empresa) -> None:
        """Associate controller with an empresa"""
        self._empresa = empresa
        empresa.add_controlador(self)

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration structure"""
        pass

    def __str__(self):
        return f"Controlador {self.name} with phone number {self.phone_number} and {len(self.signals)} signals"


class Role(Enum):
    ADMIN = "admin"
    EMPRESA_USER = "empresa_user"

class User:
    def __init__(self, first_name: str, last_name: str, email: str, password: str, role: Role):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.role = role
        self._empresa = None
        self._set_permissions()

    def _set_permissions(self):
        """Set permissions based on role"""
        self.permissions = set()
        if self.role == Role.ADMIN:
            self.permissions.update([
                'manage_users',
                'manage_empresa',
                'view_empresas',
                'manage_controller',
                'view_signals',
                'create_signals',
                'view_dashboard'
            ])
        elif self.role == Role.EMPRESA_USER:
            self.permissions.update([
                'view_empresas',
                'view_signals',
                'create_signals',
                'view_dashboard'
            ])

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def can_access_empresa(self, empresa_id: int) -> bool:
        if self.role == Role.ADMIN:
            return True
        return self._empresa and self._empresa.id == empresa_id

    @property
    def empresa(self):
        return self._empresa

    @empresa.setter
    def empresa(self, empresa):
        self._empresa = empresa

class Empresa:
    def __init__(self, name: str, phone_number: str, email: Optional[str] = None):
        self.name = name
        self._validate_phone(phone_number)
        self.phone_number = phone_number
        if email:
            self._validate_email(email)
            self.email = email
        self.users: List[User] = []
        self.controladores: List[Controlador] = []

    @staticmethod
    def _validate_phone(phone: str) -> None:
        if not phone or not phone.strip():
            raise InvalidPhoneNumber("Phone number cannot be empty")

    @staticmethod
    def _validate_email(email: str) -> None:
        if not '@' in email:
            raise InvalidEmail("Invalid email format")
        
    def add_controlador(self, controlador: Controlador) -> None:
        """Domain logic for adding controladores"""
        if any(c.phone_number == controlador.phone_number for c in self.controladores):
            raise ValueError("Controlador phone number must be unique within empresa")
        self.controladores.append(controlador)
        controlador._empresa = self  # Bidirectional relationship

    '''def add_user(self, user: User, role: Role) -> None:
        """Domain logic for adding users"""
        if any(u.email == user.email for u in self.users):
            raise ValueError("User email must be unique within empresa")
        user._empresa = self
        user.role = role
        self.users.append(user)'''
        

@dataclass
class IncomingSignalDTO:
    controlador_id: str
    sensor_values: List[int]
    location: str

    @classmethod
    def from_json(cls, data: Dict):
        return cls(
            controlador_id=data['id'],
            location=data['location'],
            sensor_values=data['sensors']
        )

class Permission(Enum):
    VIEW_DASHBOARD = 'view_dashboard'
    VIEW_SIGNALS = 'view_signals'
    MANAGE_EMPRESA = 'manage_empresa'
    MANAGE_USERS = 'manage_users'

ROLE_PERMISSIONS = {
    Role.ADMIN: [p.value for p in Permission],
    Role.EMPRESA_USER: [
        Permission.VIEW_DASHBOARD.value,
        Permission.VIEW_SIGNALS.value
    ]
}