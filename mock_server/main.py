from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
import uvicorn

from core.config import settings
from api.v1 import base as api

app = FastAPI(
    title=settings.app_title,
    default_response_class=ORJSONResponse,
)

app.include_router(api.router, prefix=settings.api_v1_prefix)

if __name__ == "__main__":
    uvicorn.run(
        'main:app',
        host=settings.project_host,
        port=settings.project_port,
    )
