from fastapi import FastAPI
from nicegui import app, ui
import logging
from ..config import settings
from .components.layout import header_and_left_drawer

from .pages import (
    home, recipe #, bindings, languages, translations
)

logger = logging.getLogger(__name__)

PAGES = [
    {'label': 'Home', 'uri': '/', 'func': home.page, 'icon': 'home'},
    {'label': 'Recipe', 'uri': '/recipe', 'func': recipe.page, 'icon': 'link'},
    # {'label': 'Languages', 'uri': '/languages', 'func': languages.page, 'icon': 'language'},
    # {'label': 'Translations', 'uri': '/translations', 'func': translations.page, 'icon': 'translate'},
    # {'label': 'Lingue', 'uri': '/languages', 'func': languages.page, 'icon': 'language'},
    # {'label': 'Traduzioni', 'uri': '/translations', 'func': translations.page, 'icon': 'translate'},
]

def init(fastapi_app: FastAPI):
    if not settings.frontend.enable:
        logger.info("Frontend is disabled in config, it will not be started.")
        return
    else:
        logger.info(f"Frontend will be available at {settings.api.public_url}{settings.frontend.prefix_path}")

    for page in PAGES:
        logger.info(f"NiceGUI Loading page: {page['label']} at {settings.api.public_url}{settings.frontend.prefix_path}{page['uri']}")
        ui.page(page['uri'])(lambda f=page['func']: header_and_left_drawer(f, PAGES))  # importante usare lambda con default arg per evitare late binding

    ui.run_with(
        fastapi_app,
        mount_path=settings.frontend.prefix_path,
        storage_secret=settings.frontend.storage_secret,
    )
