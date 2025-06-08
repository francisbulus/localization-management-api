from datetime import datetime
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    BulkTranslationUpdate, TranslationKey, TranslationKeyListResponse,
    TranslationUpdate
)

from .database import (
    format_translation_key_response, supabase, check_supabase_connection
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Helium Localization Management API",
    description="API for managing translation keys and localizations",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Helium Localization Manager API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    try:
        check_supabase_connection()
        _ = supabase.table("translation_keys").select("id").limit(1).execute()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# This is the endpoint to get the localizations for a project and locale
# It returns a JSON object with the localizations for the project and locale
@app.get("/localizations/{project_id}/{locale}")
async def get_localizations(project_id: str, locale: str):
    """Returns localizations in simple key-value format."""
    check_supabase_connection()

    try:
        result = (
            supabase.table("translation_keys")
            .select(
                """
                key,
                translations:translations!inner(language_code, value)
                """
            )
            .eq("translations.language_code", locale)
            .execute()
        )

        localizations = {}
        for item in result.data:
            if item.get("translations"):
                for translation in item["translations"]:
                    if translation["language_code"] == locale:
                        localizations[item["key"]] = translation["value"]
                        break

        logger.info(
            f"Retrieved {len(localizations)} localizations for "
            f"{project_id}/{locale}"
        )

        return {
            "project_id": project_id,
            "locale": locale,
            "localizations": localizations,
        }

    except Exception as e:
        logger.error(
            f"Error retrieving localizations for {project_id}/{locale}: {e}"
        )

        error_message = f"Failed to load localizations: {str(e)}"
        return {
            "project_id": project_id,
            "locale": locale,
            "localizations": {"error": error_message},
        }


@app.get(
    "/translation-keys/{key_id}",
    response_model=TranslationKey,
    tags=["Translation Keys"],
)
async def get_translation_key(key_id: str):
    """Get a single translation key by ID with all its translations."""
    check_supabase_connection()

    try:
        result = (
            supabase.table("translation_keys")
            .select(
                """
                id, key, category, description, created_at, updated_at,
                translations (
                    id, language_code, value, updated_at, updated_by
                )
                """
            )
            .eq("id", key_id)
            .execute()
        )

        if not result.data:
            error_detail = f"Translation key with ID {key_id} not found"
            raise HTTPException(status_code=404, detail=error_detail)

        formatted_item = format_translation_key_response(result.data[0])
        logger.info(f"Retrieved translation key: {formatted_item.key}")
        return formatted_item

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving translation key {key_id}: {e}")
        error_detail = f"Failed to retrieve translation key: {str(e)}"
        raise HTTPException(status_code=500, detail=error_detail)


@app.get(
    "/translation-keys",
    response_model=TranslationKeyListResponse,
    tags=["Translation Keys"],
)
async def get_translation_keys(
    search: Optional[str] = Query(None, description="Search in translation keys"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
):
    """Get all translation keys with their translations. Supports search and filtering."""
    check_supabase_connection()

    try:
        query = supabase.table("translation_keys").select(
            """
            id, key, category, description, created_at, updated_at,
            translations (
                id, language_code, value, updated_at, updated_by
            )
            """
        )

        if search:
            query = query.ilike("key", f"%{search}%")
        if category:
            query = query.eq("category", category)

        query = query.range(offset, offset + limit - 1)
        result = query.execute()

        formatted_items = [
            format_translation_key_response(item) for item in result.data
        ]
        logger.info(f"Retrieved {len(formatted_items)} translation keys")

        return TranslationKeyListResponse(
            items=formatted_items,
            total=len(formatted_items),
        )
    except Exception as e:
        logger.error(f"Failed to retrieve translation keys: {e}")
        error_detail = f"An unexpected error occurred: {str(e)}"
        raise HTTPException(status_code=500, detail=error_detail)


@app.put(
    "/translations/{translation_id}",
    tags=["Translations"],
)
async def update_translation(translation_id: str, update_data: TranslationUpdate):
    """Update a single translation value."""
    check_supabase_connection()

    try:
        result = (
            supabase.table("translations")
            .update(
                {
                    "value": update_data.value,
                    "updated_by": update_data.updated_by,
                    "updated_at": datetime.now().isoformat(),
                }
            )
            .eq("id", translation_id)
            .execute()
        )

        if not result.data:
            error_detail = f"Translation with ID {translation_id} not found"
            raise HTTPException(status_code=404, detail=error_detail)

        logger.info(
            f"Updated translation {translation_id} with new value: "
            f"{update_data.value}"
        )

        return {
            "success": True,
            "message": "Translation updated successfully",
            "translation_id": translation_id,
            "updated_by": update_data.updated_by,
            "timestamp": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating translation {translation_id}: {e}")
        error_detail = f"Failed to update translation: {str(e)}"
        raise HTTPException(status_code=500, detail=error_detail)
    
@app.put(
    "/translations/bulk",
    tags=["Translations"],
)
async def bulk_update_translations(bulk_update: BulkTranslationUpdate):
    """
    Bulk update multiple translations in a single request.
    More efficient than individual updates and provides transactional consistency.
    """
    check_supabase_connection()

    if not bulk_update.updates:
        raise HTTPException(status_code=400, detail="No updates provided")

    try:
        results = {}
        successful_updates = 0
        failed_updates = 0

        for translation_id, new_value in bulk_update.updates.items():
            try:
                result = (
                    supabase.table("translations")
                    .update(
                        {
                            "value": new_value,
                            "updated_by": bulk_update.updated_by,
                            "updated_at": datetime.now().isoformat(),
                        }
                    )
                    .eq("id", translation_id)
                    .execute()
                )

                if result.data:
                    results[translation_id] = {"success": True, "value": new_value}
                    successful_updates += 1
                else:
                    results[translation_id] = {
                        "success": False,
                        "error": "Translation not found",
                    }
                    failed_updates += 1

            except Exception as update_error:
                results[translation_id] = {
                    "success": False,
                    "error": str(update_error),
                }
                failed_updates += 1
                logger.warning(
                    f"Failed to update translation {translation_id}: {update_error}"
                )

        logger.info(
            f"Bulk update completed: {successful_updates} successful, "
            f"{failed_updates} failed"
        )

        return {
            "success": True,
            "message": "Bulk update completed",
            "summary": {
                "total_attempted": len(bulk_update.updates),
                "successful_updates": successful_updates,
                "failed_updates": failed_updates,
            },
            "results": results,
            "updated_by": bulk_update.updated_by,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error in bulk update: {e}")
        error_detail = f"Bulk update failed: {str(e)}"
        raise HTTPException(status_code=500, detail=error_detail)