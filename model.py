from __future__ import annotations
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import uuid


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
    tstamp: datetime
    values: Dict[str, Any]
    latitude: float
    longitude: float
    metadata: Dict[str, Any]
    _controlador: Controlador



class Controlador:
    def __init__(self, name: str, phone_number: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.phone_number = phone_number
        self.signals = []
        self._empresa: Optional[Empresa] = None

    # Maybe add some validation
    def add_signal(self, signal: Signal):
        if not isinstance(signal, Signal):
            raise InvalidSignal
        
        self.signals.append(signal)
    
    def __str__(self):
        return f"Controlador {self.name} with phone number {self.phone_number} and {len(self.signals)} signals"


class User:
    def __init__(self, first_name: str, last_name: str, email: str, password: str, phone_number: str = Optional):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.phone_number = phone_number
        self.permissions: List[str] = []
        self._empresa: Optional[Empresa] = None

    @staticmethod
    def _validate_email(email: str) -> None:
        if not '@' in email:
            raise InvalidEmail("Invalid email format")

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
    controlador_id: str  # phone number in this case
    location: str
    sensor_values: List[int]
    
    @classmethod
    def from_json(cls, data: Dict):
        return cls(
            controlador_id=data['id'],
            location=data['location'],
            sensor_values=data['sensors']
        )