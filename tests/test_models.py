import pytest
from model import User, Empresa, Controlador

def test_user():
    user = User("John", "Doe", "john.doe@example.com", "password", "1234567890")
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.email == "john.doe@example.com"
    assert user.password == "password"
    assert user.phone_number == "1234567890"

def test_empresa():
    empresa = Empresa("Empresa 1", "1234567890", "empresa1@example.com")
    assert empresa.name == "Empresa 1"
    assert empresa.phone_number == "1234567890"
    assert empresa.email == "empresa1@example.com"

def test_controlador():
    controlador = Controlador("Controlador 1", "1234567890", config={})
    assert controlador.name == "Controlador 1"
    assert controlador.phone_number == "1234567890"


