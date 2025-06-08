# Helium Localization Management API

A FastAPI backend for managing translation keys and localizations, built for the Helium take-home assignment.

## Architecture Overview

### Key Design Decisions

**Database Schema**: Normalized design with separate `translation_keys` and `translations` tables for scalability and data integrity.

**Error Handling Strategy**:

- `422` for validation errors (Pydantic)
- `400` for business logic violations
- `404` for resource not found
- `500` for server errors with graceful degradation

**Performance Optimizations**:

- Database indexes on frequently queried columns
- Efficient joins to minimize round trips
- Pagination for large datasets

## Quick Start

### Prerequisites

```bash
# Required
Python 3.8+
Supabase account (free tier)
```

### Installation

```bash
# Clone and setup
git clone <repository-url>
cd localization-management-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Database Setup

1. **Create Supabase Project**: Visit [supabase.com](https://supabase.com) and create a new project
2. **Run Schema Setup**: Execute the following SQL in your Supabase SQL editor:

```sql
-- Translation Keys Table
CREATE TABLE translation_keys (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    key TEXT NOT NULL UNIQUE,
    category TEXT,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Translations Table
CREATE TABLE translations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    translation_key_id UUID REFERENCES translation_keys(id) ON DELETE CASCADE,
    language_code TEXT NOT NULL,
    value TEXT NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_by TEXT DEFAULT 'system',
    UNIQUE(translation_key_id, language_code)
);

-- Performance Indexes
CREATE INDEX idx_translation_keys_key ON translation_keys(key);
CREATE INDEX idx_translation_keys_category ON translation_keys(category);
CREATE INDEX idx_translations_language ON translations(language_code);
CREATE INDEX idx_translations_key_lang ON translations(translation_key_id, language_code);
```

3. **Load Sample Data**: Execute the sample data inserts provided in the repository

### Environment Configuration

```bash
# Create .env file
cp .env.example .env

SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key-here
```

### Run the Server

```bash
python -m uvicorn src.localization_management_api.main:app --reload
```

**API Documentation**: Visit `http://localhost:8000/docs` for interactive Swagger UI

## API Reference

### Management Endpoints

#### Translation Keys

```http
GET /translation-keys
```

**Query Parameters**:

- `search` - Filter by key name (case-insensitive)
- `category` - Filter by category
- `limit` - Results per page (default: 100, max: 1000)
- `offset` - Skip results for pagination

**Response**: Structured data with metadata

```json
{
  "items": [
    {
      "id": "uuid",
      "key": "button.save",
      "category": "buttons",
      "description": "Save button text",
      "translations": [
        {
          "id": "uuid",
          "language_code": "en",
          "value": "Save",
          "updated_by": "user",
          "updated_at": "2025-01-01T00:00:00Z"
        }
      ],
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    }
  ],
  "total": 150
}
```

```http
GET /translation-keys/{id}
```

**Response**: Single translation key with all translations

```http
PUT /translations/{translation_id}
```

**Body**:

```json
{
  "value": "Updated translation",
  "updated_by": "user_id"
}
```

#### NEW FEATURE: Bulk Operations

```http
PUT /translations/bulk
```

**Body**:

```json
{
  "updates": {
    "translation_id_1": "New value 1",
    "translation_id_2": "New value 2"
  },
  "updated_by": "bulk_user"
}
```

**Response**:

```json
{
  "success": true,
  "summary": {
    "total_attempted": 2,
    "successful_updates": 2,
    "failed_updates": 0
  },
  "results": {
    "translation_id_1": { "success": true, "value": "New value 1" },
    "translation_id_2": { "success": true, "value": "New value 2" }
  },
  "updated_by": "bulk_user",
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### Consumer Endpoints

#### Localizations (Enhanced Legacy)

```http
GET /localizations/{project_id}/{locale}
```

**Response**: Optimized key-value pairs for application consumption. The project_id parameter is echoed back in the response but currently not used for filtering - all translations for the specified locale are returned regardless of project.

```json
{
  "project_id": "my-app",
  "locale": "en",
  "localizations": {
    "button.save": "Save",
    "button.cancel": "Cancel",
    "welcome.title": "Welcome!"
  }
}
```

### Health & Monitoring

```http
GET /health
```

**Response**: System health with database connectivity status

## Implementation Details

### File Structure

```
src/localization_management_api/
├── main.py          # FastAPI app, routes, middleware
├── models.py        # Pydantic request/response models
├── database.py      # Supabase client and data layer
└── __init__.py

tests/
├── conftest.py      # Test fixtures and configuration
├── test_endpoints.py    # API endpoint tests
└── test_performance.py  # Performance tests
```

### Data Layer (`database.py`)

- **Connection Management**: Supabase client initialization
- **Query Structure**: Database joins with proper field selection
- **Error Handling**: Basic error catching with logging
- **Data Formatting**: Conversion between database and API models

### Request/Response Models (`models.py`)

- **Validation**: Pydantic models with field validation
- **Type Safety**: TypeScript-compatible type definitions
- **API Documentation**: Auto-generated OpenAPI specs

### API Layer (`main.py`)

- **Route Organization**: Logical grouping with tags
- **Middleware**: CORS configuration
- **Error Handling**: HTTP exception handling

## Testing

### Run Test Suite

```bash
# All tests
pytest

# Specific test categories
pytest tests/test_endpoints.py -v
pytest tests/test_performance.py -v
```

### Test Categories

- **Endpoint Tests**: CRUD operation coverage
- **Performance Tests**: Basic performance validation
- **Error Handling**: Edge cases and failure scenarios

### Mock Strategy

- **Supabase Client**: Mocked for deterministic tests
- **Database Responses**: Sample data for testing

## Assignment Compliance

### Requirements Fulfilled

✅ **Enhanced Existing Endpoints**: Original `/localizations` endpoint enhanced with database integration  
✅ **Query by ID and List**: CRUD operations with search and filtering  
✅ **Supabase Integration**: Database client usage with queries  
✅ **Bulk Update Feature**: Bulk update endpoint with individual success/failure tracking  
✅ **Targeted Tests**: Test suite covering API functionality and performance

---

**Built with**: FastAPI, Pydantic, Supabase, PostgreSQL, Pytest  
**Assignment Duration**: 3 hours  
**Focus**: Backend engineering and API design
