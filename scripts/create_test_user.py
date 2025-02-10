from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.services.auth_service import AuthService
from src.domain.model import Role
from src.config import get_postgres_uri
from src.adapters.orm import start_mappers

def create_test_users():
    # Initialize SQLAlchemy mappers
    start_mappers()
    
    # Setup database connection
    engine = create_engine(get_postgres_uri())
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Create auth service
    auth_service = AuthService(session)
    
    try:
        # Create test admin user
        admin_data = {
            "first_name": "Admin",
            "last_name": "User",
            "email": "admin@test.com",
            "password": "admin123",
            "role": Role.ADMIN
        }
        
        # Create test empresa user
        empresa_user_data = {
            "first_name": "Empresa",
            "last_name": "User",
            "email": "empresa@test.com",
            "password": "empresa123",
            "role": Role.EMPRESA_USER
        }
        
        # Register users
        admin = auth_service.register_user(admin_data)
        empresa_user = auth_service.register_user(empresa_user_data)
        
        # Verify permissions were set correctly
        print("\nCreated users:")
        print(f"Admin: {admin.email}")
        print(f"- Role: {admin.role}")
        print(f"- Permissions: {admin.permissions}")
        print(f"\nEmpresa User: {empresa_user.email}")
        print(f"- Role: {empresa_user.role}")
        print(f"- Permissions: {empresa_user.permissions}")
        
        session.commit()
        print("\nTest users created successfully!")
        
    except Exception as e:
        print(f"Error creating users: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    create_test_users() 