from src.domain.model import Empresa, User, Role
from uuid import UUID
from werkzeug.security import generate_password_hash

def create_initial_data(session):
    """Create initial test data if it doesn't exist"""
    
    # Check if test empresa exists
    test_empresa_id = UUID('b8cdf279-d884-4db1-aa2c-eb8d7e4c41bf')
    existing_empresa = session.query(Empresa).filter_by(id=test_empresa_id).first()
    
    if not existing_empresa:
        # Create test empresa
        test_empresa = Empresa(
            id=test_empresa_id,
            name="Test Compania loke",
            phone_number="1234567890",
            email="test@company.com"
        )
        session.add(test_empresa)
        
        # Create test admin user
        admin_user = User(
            email="admin@test.com",
            password_hash=generate_password_hash("admin123"),
            role=Role.ADMIN,
            empresa=test_empresa
        )
        session.add(admin_user)
        
        session.commit()
        print("Initial test data created successfully!") 