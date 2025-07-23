from .config import settings
import logging
import uvicorn

from .main import app

def dev():
    logging.info("Starting Hypercorn DEV mode")
    uvicorn.run(
        "legends_cookbook.main:app",  # path al tuo oggetto FastAPI
        host=settings.api.host,
        port=settings.api.port,
        reload=True,
        log_level=settings.logging.level.lower(),
        factory=False  # se app è già creato
    )


def main():
    logging.info("Starting Hypercorn")
    uvicorn.run(
        "legends_cookbook.main:app",  # path al tuo oggetto FastAPI
        host=settings.api.host,
        port=settings.api.port,
        reload=False,
        log_level=settings.logging.level.lower(),
        factory=False  # se app è già creato
    )