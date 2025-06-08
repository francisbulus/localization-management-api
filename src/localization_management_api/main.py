import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import supabase, check_supabase_connection

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
