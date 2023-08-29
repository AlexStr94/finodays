import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from api.v1 import base as api
from core.config import app_settings

app = FastAPI(
    title=app_settings.app_title,
    default_response_class=ORJSONResponse,
)

app.include_router(api.router, prefix=app_settings.api_v1_prefix)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(
        'main:app',
        host=app_settings.project_host,
        port=app_settings.project_port,
    )
