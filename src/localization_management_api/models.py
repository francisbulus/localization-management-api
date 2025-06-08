from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class Translation(BaseModel):
    id: str
    language_code: str
    value: str
    updated_at: str
    updated_by: str


class TranslationKey(BaseModel):
    id: str
    key: str
    category: str
    description: Optional[str] = None
    translations: List[Translation]
    created_at: str
    updated_at: str


class TranslationKeyListResponse(BaseModel):
    items: List[TranslationKey]
    total: int


class TranslationUpdate(BaseModel):
    value: str
    updated_by: str = "user"


class BulkTranslationUpdate(BaseModel):
    updates: Dict[str, str] = Field(..., description="Dictionary of translation_id: new_value")
    updated_by: str = "bulk_user"
