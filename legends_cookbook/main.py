from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi import Depends, Query
from typing import List, Optional
import logging
import sys
import traceback

from .config import settings
from .db import wait_for_db, connect_db, get_db

fileHandler = logging.FileHandler(f"{settings.logging.prefix}{__name__}.log", mode='a')
logging.basicConfig(
    level=getattr(logging, settings.logging.level, 'DEBUG'),
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        fileHandler
    ]
)

@asynccontextmanager
async def lifetime_hook(app: FastAPI):
    try:
        if wait_for_db():
            connect_db()
    except TimeoutError:
        logging.error(f"Unable to connect to database!")
        exit(1)
    
    logging.info("App started!")

    # Wait until app end
    yield

    # Cleanup stuff if need be ..
    logging.info("App shutdown...")


# Initialize FastAPI
app = FastAPI(
    title="LocaleAPI",
    description=f"👉 Vai all'interfaccia grafica: [GUI]({settings.frontend.prefix_path})",
    openapi_tags=[
        {"name": "Bindings", "description": "Operazioni sui bindings"},
    ],
    lifespan=lifetime_hook
)

# from .api.v1 import (bindings_router, languages_router, translations_router, functions_router)

# app.include_router(bindings_router, prefix=f"{settings.api.prefix_path}/bindings", tags=["Bindings"])
# app.include_router(languages_router, prefix=f"{settings.api.prefix_path}/languages", tags=["Languages"])
# app.include_router(translations_router, prefix=f"{settings.api.prefix_path}/translations", tags=["Translations"])
# app.include_router(functions_router, prefix=f"{settings.api.prefix_path}/functions", tags=["Functions"])

from .frontend.main import init as init_frontend
init_frontend(app)

@app.get('/')
@app.get(f"{settings.api.prefix_path}/status")
def api_status():
    return JSONResponse(status_code=200,
        content=[
                dict(prefix=f"/docs", tags=["Swagger UI"]),
                # dict(prefix=f"{settings.api.prefix_path}/bindings", tags=["Bindings"]),
                # dict(prefix=f"{settings.api.prefix_path}/languages", tags=["Languages"]),
                # dict(prefix=f"{settings.api.prefix_path}/translations", tags=["Translations"]),
                # dict(prefix=f"{settings.api.prefix_path}/functions", tags=["Functions"])
            ]
    )

@app.middleware("http")
async def error_handling_middleware(request, call_next):
    try:
        response = await call_next(request)
        return response
    except HTTPException as e:
        pass
    except Exception as e:
        logging.error(f"Unhandled error: {e} Traceback: { traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "error": str(e), "traceback": traceback.format_exc()}
        )