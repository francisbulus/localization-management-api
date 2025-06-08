import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from src.localization_management_api.main import app

MOCK_TRANSLATION_KEYS = [
    {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "key": "button.save",
        "category": "buttons", 
        "description": "Save button text",
        "created_at": "2025-01-01T00:00:00+00:00",
        "updated_at": "2025-01-01T00:00:00+00:00",
        "translations": [
            {
                "id": "456e7890-e89b-12d3-a456-426614174001",
                "language_code": "en",
                "value": "Save",
                "updated_at": "2025-01-01T00:00:00+00:00",
                "updated_by": "system"
            },
            {
                "id": "789e0123-e89b-12d3-a456-426614174002", 
                "language_code": "es",
                "value": "Guardar",
                "updated_at": "2025-01-01T00:00:00+00:00",
                "updated_by": "system"
            }
        ]
    },
    {
        "id": "234e5678-e89b-12d3-a456-426614174003",
        "key": "button.cancel", 
        "category": "buttons",
        "description": "Cancel button text",
        "created_at": "2025-01-01T00:00:00+00:00",
        "updated_at": "2025-01-01T00:00:00+00:00",
        "translations": [
            {
                "id": "567e8901-e89b-12d3-a456-426614174004",
                "language_code": "en", 
                "value": "Cancel",
                "updated_at": "2025-01-01T00:00:00+00:00",
                "updated_by": "system"
            }
        ]
    }
]

@pytest.fixture
def client():
    """Test client for FastAPI app"""
    return TestClient(app)

@pytest.fixture
def mock_supabase():
    """Mock Supabase client with common responses"""
    mock_client = Mock()
    
    mock_table = Mock()
    mock_client.table.return_value = mock_table
    

    mock_table.select.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.ilike.return_value = mock_table
    mock_table.range.return_value = mock_table
    mock_table.update.return_value = mock_table
    

    mock_table.execute.return_value = Mock(data=MOCK_TRANSLATION_KEYS)
    
    return mock_client

@pytest.fixture
def mock_supabase_connection():
    """Mock the check_supabase_connection function"""
    with patch('src.localization_management_api.database.check_supabase_connection'):
        yield