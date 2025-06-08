from fastapi import FastAPI

app = FastAPI()

## This is the endpoint to get the localizations for a project and locale
## It returns a JSON object with the localizations for the project and locale
@app.get("/localizations/{project_id}/{locale}")
async def get_localizations(project_id: str, locale: str):
    return {"project_id": project_id, "locale": locale, "localizations": {"greeting": "Hello", "farewell": "Goodbye"}}
