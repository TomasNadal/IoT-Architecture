import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_auth():
    # 1. Try to login
    login_data = {
        "email": "admin@test.com",
        "password": "admin123"
    }
    
    # Login request
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print("\nLogin Response:", response.status_code)
    print(response.json())
    
    if response.status_code == 200:
        token = response.json()['token']
        
        # Try accessing protected endpoint
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Test empresas endpoint
        response = requests.get(f"{BASE_URL}/empresas", headers=headers)
        print("\nProtected Endpoint Response:", response.status_code)
        print(response.json())
        
        # Test without token
        response = requests.get(f"{BASE_URL}/empresas")
        print("\nUnauthorized Request Response:", response.status_code)
        print(response.json())

if __name__ == "__main__":
    test_auth() 