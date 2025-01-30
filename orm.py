from sqlalchemy import Table, MetaData, Column, Integer, String, Date, ForeignKey, Float, DateTime
from sqlalchemy.dialects.postgresql import JSONB  # Import JSONB type
from sqlalchemy.orm import registry, relationship, attribute_keyed_dict


import model as m

'''
Metadata contains information of the database schema
'''
mapper_registry = registry()

# Define tables
signals = Table(
    'signals',
    mapper_registry.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('controlador_id', Integer, ForeignKey('controladores.id')),
    Column('tstamp', DateTime, nullable=False),
    Column('values', JSONB, nullable=False),  # Changed from JSON to JSONB
    Column('latitude', Float, nullable=False),
    Column('longitude', Float, nullable=False),
    Column('metadata', JSONB, nullable=False)  # Changed from JSON to JSONB
)


controladores = Table(
    'controladores',
    mapper_registry.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('empresa_id', Integer, ForeignKey('empresas.id')),
    Column('name', String(255), nullable=False),
    Column('config', JSONB, nullable=False),  # Changed from JSON to JSONB
    Column('phone_number', String(20), nullable=False)
)

users = Table(
    'users',
    mapper_registry.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('empresa_id', Integer, ForeignKey('empresas.id')),
    Column('first_name', String(255), nullable=False),
    Column('last_name', String(255), nullable=False),
    Column('email', String(255), nullable=False, unique=True),
    Column('password', String(255), nullable=False),
    Column('phone_number', String(20), nullable=True)
)

empresas = Table(
    'empresas',
    mapper_registry.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(255), nullable=False),
    Column('phone_number', String(20), nullable=False),
    Column('email', String(255), nullable=False)
)

def start_mappers():
    # Map Signal
    signals_mapper = mapper_registry.map_imperatively(
        m.Signal,
        signals,
        properties={
            "_controlador": relationship("Controlador", back_populates="signals")
        }
    )

    # Map Controlador
    controladores_mapper = mapper_registry.map_imperatively(
        m.Controlador,
        controladores,
        properties={
            "signals": relationship(signals_mapper, collection_class=list, back_populates="_controlador"),
            "_empresa": relationship("Empresa", back_populates="controladores")
        }
    )

    # Map User
    users_mapper = mapper_registry.map_imperatively(
        m.User,
        users,
        properties={
            "_empresa": relationship("Empresa", back_populates="users")
        }
    )

    # Map Empresa
    mapper_registry.map_imperatively(
        m.Empresa,
        empresas,
        properties={
            "users": relationship(users_mapper, collection_class=list, back_populates="_empresa"),
            "controladores": relationship(controladores_mapper, collection_class=list, back_populates="_empresa")
        }
    )