import os
from dotenv import load_dotenv
from supabase import create_client, Client
from fastapi import HTTPException
from typing import Dict, Any
import logging
from .models import TranslationKey, Translation


load_dotenv()

logger = logging.getLogger(__name__)


def get_supabase_client() -> Client:
    """Initialize and return Supabase client"""
    try:
        supabase = create_client(
            os.getenv("SUPABASE_URL", ""), 
            os.getenv("SUPABASE_SERVICE_KEY", "")
        )
        logger.info("Supabase client initialized successfully")
        return supabase
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")


supabase = get_supabase_client()


def check_supabase_connection():
    """Check if Supabase client is available"""
    if supabase is None:
        raise HTTPException(
            status_code=500, 
            detail="Database connection not available. Please check Supabase configuration."
        )


def format_translation_key_response(raw_data: Dict[str, Any]) -> TranslationKey:
    """Format raw database response into TranslationKey model"""
    translations = []

    for translation in raw_data.get("translations", []):
        translations.append(Translation(
            id=translation["id"],
            language_code=translation["language_code"],
            value=translation["value"],
            updated_at=translation["updated_at"],
            updated_by=translation["updated_by"]
        ))

    return TranslationKey(
        id=raw_data["id"],
        key=raw_data["key"],
        category=raw_data["category"] or "",
        description=raw_data.get("description"),
        translations=translations,
        created_at=raw_data["created_at"],
        updated_at=raw_data["updated_at"]
    )
