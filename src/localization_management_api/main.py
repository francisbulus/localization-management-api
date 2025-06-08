import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from localization_management_api.models import TranslationKey

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
