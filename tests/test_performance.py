import pytest
import time
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from src.localization_management_api.main import app


class TestDatabaseQueryPerformance:
    """Test database query performance with sample data"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def large_dataset_mock(self):
        """Mock large dataset for performance testing"""
        large_dataset = []
        for i in range(1000):
            large_dataset.append({
                "id": f"key-{i:04d}",
                "key": f"sample.key.{i}",
                "category": f"category_{i % 10}",
                "description": f"Sample translation key {i}",
                "created_at": "2025-01-01T00:00:00+00:00",
                "updated_at": "2025-01-01T00:00:00+00:00",
                "translations": [
                    {
                        "id": f"trans-{i}-en",
                        "language_code": "en",
                        "value": f"English value {i}",
                        "updated_at": "2025-01-01T00:00:00+00:00",
                        "updated_by": "system"
                    },
                    {
                        "id": f"trans-{i}-es", 
                        "language_code": "es",
                        "value": f"Valor en español {i}",
                        "updated_at": "2025-01-01T00:00:00+00:00",
                        "updated_by": "system"
                    },
                    {
                        "id": f"trans-{i}-fr",
                        "language_code": "fr", 
                        "value": f"Valeur française {i}",
                        "updated_at": "2025-01-01T00:00:00+00:00",
                        "updated_by": "system"
                    }
                ]
            })
        return large_dataset
    
    @patch('src.localization_management_api.main.supabase')
    @patch('src.localization_management_api.database.check_supabase_connection')
    def test_large_dataset_query_performance(self, mock_check, mock_supabase, client, large_dataset_mock):
        """Test query performance with large dataset (1000+ keys)"""
        mock_table = Mock()
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.ilike.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.range.return_value = mock_table
        mock_table.execute.return_value = Mock(data=large_dataset_mock)
        
        start_time = time.time()
        response = client.get("/translation-keys?limit=1000")
        end_time = time.time()
        
        query_time = end_time - start_time
        assert query_time < 2.0, f"Query took {query_time:.2f}s, should be under 2s"
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["items"]) == 1000
        assert data["total"] == 1000
    
    @patch('src.localization_management_api.main.supabase')
    @patch('src.localization_management_api.database.check_supabase_connection')
    def test_search_query_performance(self, mock_check, mock_supabase, client, large_dataset_mock):
        """Test search query performance with large dataset"""
        # Filter dataset to simulate search results (50 matches)
        search_results = [item for item in large_dataset_mock[:50] if "sample.key.1" in item["key"]]
        
        mock_table = Mock()
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.ilike.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.range.return_value = mock_table
        mock_table.execute.return_value = Mock(data=search_results)
        
        start_time = time.time()
        response = client.get("/translation-keys?search=sample.key.1")
        end_time = time.time()
        
        query_time = end_time - start_time
        assert query_time < 1.0, f"Search query took {query_time:.2f}s, should be under 1s"
        assert response.status_code == 200
        
        mock_table.ilike.assert_called_with("key", "%sample.key.1%")
    
    @patch('src.localization_management_api.main.supabase')
    @patch('src.localization_management_api.database.check_supabase_connection')
    def test_localizations_endpoint_performance(self, mock_check, mock_supabase, client):
        """Test localizations endpoint performance with large dataset"""
        localization_data = []
        for i in range(500):
            localization_data.append({
                "key": f"app.text.{i}",
                "translations": [
                    {"language_code": "en", "value": f"English text {i}"}
                ]
            })
        
        mock_table = Mock()
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.execute.return_value = Mock(data=localization_data)
        
        start_time = time.time()
        response = client.get("/localizations/large-app/en")
        end_time = time.time()
        
        query_time = end_time - start_time
        assert query_time < 1.5, f"Localization query took {query_time:.2f}s, should be under 1.5s"
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["localizations"]) == 500
        assert data["project_id"] == "large-app"
        assert data["locale"] == "en"


class TestBulkUpdatePerformance:
    """Test NEW FEATURE bulk update performance"""
    
    @pytest.fixture  
    def client(self):
        return TestClient(app)

    
    @patch('src.localization_management_api.main.supabase')
    @patch('src.localization_management_api.database.check_supabase_connection')
    def test_individual_update_performance(self, mock_check, mock_supabase, client):
        """Test individual update performance as baseline"""
        mock_table = Mock()
        mock_supabase.table.return_value = mock_table
        mock_table.update.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[{"id": "test", "value": "updated"}])
        
        update_data = {
            "value": "Performance test value",
            "updated_by": "test_user"
        }
        
        start_time = time.time()
        response = client.put("/translations/550e8400-e29b-41d4-a716-446615174000", json=update_data)
        end_time = time.time()

        update_time = end_time - start_time
        assert update_time < 1.0, f"Individual update took {update_time:.2f}s, should be under 1s"
        assert response.status_code == 200



class TestConcurrentRequestPerformance:
    """Test API performance under concurrent load"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @patch('src.localization_management_api.main.supabase')
    @patch('src.localization_management_api.database.check_supabase_connection')
    def test_concurrent_read_requests(self, mock_check, mock_supabase, client):
        """Test multiple concurrent read requests"""
        mock_table = Mock()
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.ilike.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.range.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[])
        
        import threading
        import time
        
        results = []
        start_time = time.time()
        
        def make_request():
            response = client.get("/translation-keys?limit=50")
            results.append(response.status_code)
        
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        assert total_time < 5.0, f"10 concurrent requests took {total_time:.2f}s, should be under 5s"
        assert all(status == 200 for status in results), "All concurrent requests should succeed"
        assert len(results) == 10, "All 10 requests should complete"


class TestMemoryUsageEfficiency:
    """Test memory efficiency with large datasets"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @patch('src.localization_management_api.main.supabase')
    @patch('src.localization_management_api.database.check_supabase_connection')
    def test_pagination_memory_efficiency(self, mock_check, mock_supabase, client):
        """Test that pagination limits memory usage"""
        mock_table = Mock()
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.ilike.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.range.return_value = mock_table

        paginated_data = []
        for i in range(50):
            paginated_data.append({
                "id": f"550e8400-e29b-41d4-a716-44661517{i:04d}",
                "key": f"test.key.{i}",
                "category": f"category_{i % 5}",
                "description": f"Test key {i}", 
                "created_at": "2025-01-01T00:00:00+00:00",
                "updated_at": "2025-01-01T00:00:00+00:00",
                "translations": []
            })
        mock_table.execute.return_value = Mock(data=paginated_data)
        
        response = client.get("/translation-keys?limit=50&offset=100")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["items"]) == 50, "Should return exactly 50 items despite large dataset"
        
        mock_table.range.assert_called_with(100, 149)  # offset to offset + limit - 1
    
    @patch('src.localization_management_api.main.supabase')
    @patch('src.localization_management_api.database.check_supabase_connection')
    def test_query_result_size_optimization(self, mock_check, mock_supabase, client):
        """Test that queries only return necessary data"""
        mock_table = Mock()
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[])
        
        client.get("/localizations/test-app/en")
        
        mock_table.select.assert_called()

        select_call = mock_table.select.call_args[0][0]
        assert "description" not in select_call
        assert "created_at" not in select_call