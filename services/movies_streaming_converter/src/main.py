import logging

from api.v1 import convertation
from core.config.api import get_config
from db.connections import close_connections, init_connections
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse

config = get_config()

app = FastAPI(
    title=config.app_project_name,
    docs_url="/convert_api/openapi",
    openapi_url="/convert_api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    await init_connections()


@app.on_event("shutdown")
async def shutdown():
    await close_connections()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level=logging.DEBUG,
    )
