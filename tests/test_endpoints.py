from unittest.mock import patch, Mock
from fastapi import status


class TestBasicEndpoints:
    
    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["message"] == "Helium Localization Manager API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"


class TestTranslationKeysEndpoints:
    
    @patch('src.localization_management_api.main.supabase')
    def test_get_translation_keys_success(self, mock_supabase, client, mock_supabase_connection):
        mock_table = Mock()
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.ilike.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.range.return_value = mock_table
        
        mock_data = [
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
                    }
                ]
            }
        ]
        mock_table.execute.return_value = Mock(data=mock_data)
        
        response = client.get("/translation-keys")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) == 1
        assert data["items"][0]["key"] == "button.save"
    
    @patch('src.localization_management_api.main.supabase')
    def test_get_translation_keys_with_search(self, mock_supabase, client, mock_supabase_connection):
        mock_table = Mock()
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.ilike.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.range.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[])
        
        response = client.get("/translation-keys?search=button")
        assert response.status_code == status.HTTP_200_OK
        
        mock_table.ilike.assert_called_with("key", "%button%")
    
    @patch('src.localization_management_api.main.supabase')
    def test_get_translation_key_by_id_success(self, mock_supabase, client, mock_supabase_connection):
        mock_table = Mock()
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        
        mock_data = [{
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "key": "button.save",
            "category": "buttons",
            "description": "Save button text",
            "created_at": "2025-01-01T00:00:00+00:00", 
            "updated_at": "2025-01-01T00:00:00+00:00",
            "translations": []
        }]
        mock_table.execute.return_value = Mock(data=mock_data)
        
        key_id = "123e4567-e89b-12d3-a456-426614174000"
        response = client.get(f"/translation-keys/{key_id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == key_id
        assert data["key"] == "button.save"
    
    @patch('src.localization_management_api.main.supabase')
    def test_get_translation_key_not_found(self, mock_supabase, client, mock_supabase_connection):
        mock_table = Mock()
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[])
        
        response = client.get("/translation-keys/nonexistent-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestTranslationUpdateEndpoints:
    
    @patch('src.localization_management_api.main.supabase')
    def test_update_translation_success(self, mock_supabase, client, mock_supabase_connection):
        mock_table = Mock()
        mock_supabase.table.return_value = mock_table
        mock_table.update.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[{"id": "test-id", "value": "Updated"}])
        
        update_data = {
            "value": "Updated Save",
            "updated_by": "test_user"
        }
        
        response = client.put("/translations/test-id", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["success"] is True
        assert data["translation_id"] == "test-id"
        assert data["updated_by"] == "test_user"
    
    @patch('src.localization_management_api.main.supabase')
    def test_update_translation_not_found(self, mock_supabase, client, mock_supabase_connection):
        mock_table = Mock()
        mock_supabase.table.return_value = mock_table
        mock_table.update.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[])
        
        update_data = {
            "value": "Updated Save",
            "updated_by": "test_user"
        }
        
        response = client.put("/translations/nonexistent-id", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestBulkUpdateEndpoint:
    
    def test_bulk_update_empty_updates_validation(self, client, mock_supabase_connection):
        bulk_data = {
            "updates": {},
            "updated_by": "test_user"
        }
        
        response = client.put("/translations/bulk", json=bulk_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_bulk_update_missing_field_validation(self, client, mock_supabase_connection):
        bulk_data = {
            "updated_by": "test_user"
        }
        
        response = client.put("/translations/bulk", json=bulk_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLocalizationsEndpoint:
    
    @patch('src.localization_management_api.main.supabase')
    def test_get_localizations_success(self, mock_supabase, client, mock_supabase_connection):
        mock_table = Mock()
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        
        mock_data = [
            {
                "key": "button.save",
                "translations": [
                    {"language_code": "en", "value": "Save"}
                ]
            },
            {
                "key": "button.cancel", 
                "translations": [
                    {"language_code": "en", "value": "Cancel"}
                ]
            }
        ]
        mock_table.execute.return_value = Mock(data=mock_data)
        
        response = client.get("/localizations/test-project/en")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["project_id"] == "test-project"
        assert data["locale"] == "en"
        assert data["localizations"]["button.save"] == "Save"
        assert data["localizations"]["button.cancel"] == "Cancel"
    
    @patch('src.localization_management_api.main.supabase')
    def test_get_localizations_database_error(self, mock_supabase, client, mock_supabase_connection):
        mock_table = Mock()
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.execute.side_effect = Exception("Database connection failed")
        
        response = client.get("/localizations/test-project/en")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["project_id"] == "test-project"
        assert data["locale"] == "en"
        assert "error" in data["localizations"]