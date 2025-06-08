from pydantic import BaseModel, Field, field_validator
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
    updates: Dict[str, str] = Field(
        ...,
        description="Dictionary of translation_id: new_value",
        min_length=1
    )
    updated_by: str = "bulk_user"
    
    @field_validator('updates')
    @classmethod
    def validate_updates_not_empty(cls, v):
        if not v:
            raise ValueError('Updates dictionary cannot be empty')
        return v

    @field_validator('updates')
    @classmethod 
    def validate_translation_ids(cls, v):
        for translation_id in v.keys():
            if not translation_id.strip():
                raise ValueError('Translation ID cannot be empty or whitespace')
        return v