import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_full_flow():
    # 1. Login as admin
    print("\n1. Testing Admin Login...")
    login_data = {
        "email": "admin@test.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print("Login Response:", response.status_code)
    print(response.json())
    
    if response.status_code != 200:
        print("Login failed!")
        return
        
    token = response.json()['token']
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 2. Create a new empresa
    print("\n2. Creating new empresa...")
    empresa_data = {
        "name": "Test Company",
        "phone_number": "1234567890",
        "email": "company@test.com"
    }
    
    response = requests.post(
        f"{BASE_URL}/empresas/", 
        headers=headers,
        json=empresa_data
    )
    print("Create Empresa Response:", response.status_code)
    print(response.json())
    
    if response.status_code == 201:
        empresa_id = response.json().get('id')
        
        # 3. Create a controlador for the empresa
        print("\n3. Creating new controlador...")
        controlador_data = {
            "empresa_id": empresa_id,
            "name": "Test Controller",
            "phone_number": "9876543210",
            "config": {
                "sampling_rate": 60,
                "threshold": 25.5
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/controladores",
            headers=headers,
            json=controlador_data
        )
        print("Create Controlador Response:", response.status_code)
        print(response.json())
        
        if response.status_code == 201:
            controlador_id = response.json().get('id')
            
            # 4. Test sending a signal
            print("\n4. Sending test signal...")
            signal_data = {
                "controlador_id": controlador_id,
                "sensor_values": [24.5, 26.7, 25.1],
                "location": "Test Location"
            }
            
            response = requests.post(
                f"{BASE_URL}/signals",
                headers=headers,
                json=signal_data
            )
            print("Send Signal Response:", response.status_code)
            print(response.json())
            
            # 5. Get dashboard data
            print("\n5. Getting dashboard data...")
            response = requests.get(
                f"{BASE_URL}/dashboard/empresa/{empresa_id}/dashboard",
                headers=headers
            )
            print("Dashboard Response:", response.status_code)
            print(response.json())

if __name__ == "__main__":
    test_full_flow() 