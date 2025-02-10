import pytest
import requests
from flask import url_for

# Configure base URL for tests
BASE_URL = 'http://localhost:5000'  # Adjust according to your setup

@pytest.fixture
def client():
    from entrypoints.flask_app import app  # Import your Flask app
    with app.test_client() as client:
        yield client

def test_create_chat_returns_201_and_chat_id(client):
    """Test creating a new chat session"""
    response = client.post('/chat/create')
    
    assert response.status_code == 201
    assert 'chat_id' in response.json
    assert response.json['chat_id'] is not None

def test_send_message_returns_200_and_response(client):
    """Test sending a message and getting a response"""
    # First create a chat
    chat_response = client.post('/chat/create')
    chat_id = chat_response.json['chat_id']
    
    # Then send a message
    message_data = {
        'chat_id': chat_id,
        'message': 'Hello, AI!',
        'role': 'user'
    }
    
    response = client.post('/chat/send', json=message_data)
    
    assert response.status_code == 200
    assert 'response' in response.json
    assert response.json['response'] is not None

def test_get_chat_history_returns_200_and_messages(client):
    """Test retrieving chat history"""
    # First create a chat
    chat_response = client.post('/chat/create')
    chat_id = chat_response.json['chat_id']
    
    # Send a message
    message_data = {
        'chat_id': chat_id,
        'message': 'Hello, AI!',
        'role': 'user'
    }
    client.post('/chat/send', json=message_data)
    
    # Get chat history
    response = client.get(f'/chat/{chat_id}/history')
    
    assert response.status_code == 200
    assert 'messages' in response.json
    assert isinstance(response.json['messages'], list)
    assert len(response.json['messages']) > 0

def test_invalid_chat_id_returns_404(client):
    """Test handling of invalid chat ID"""
    response = client.get('/chat/invalid_id/history')
    assert response.status_code == 404

def test_invalid_message_format_returns_400(client):
    """Test handling of invalid message format"""
    message_data = {
        'chat_id': 'some_id',
        # Missing required 'message' field
        'role': 'user'
    }
    
    response = client.post('/chat/send', json=message_data)
    assert response.status_code == 400

@pytest.mark.parametrize('role', ['invalid_role', '123', ''])
def test_invalid_role_returns_400(client, role):
    """Test handling of invalid role values"""
    chat_response = client.post('/chat/create')
    chat_id = chat_response.json['chat_id']
    
    message_data = {
        'chat_id': chat_id,
        'message': 'Hello',
        'role': role
    }
    
    response = client.post('/chat/send', json=message_data)
    assert response.status_code == 400
