from nicegui import ui
from typing import Callable

from ...config import settings
from .login_interface import component as login_btn


def header_and_left_drawer(page_func: Callable, pages: list[dict]):
    darkmode = ui.dark_mode()

    with ui.left_drawer(top_corner=False, elevated=True, value=False).props('bordered') as drawer:
        with ui.column().classes('w-full'):
            ui.label('Navigation').classes('text-grey text-caption ml-2 mt-2')
            for page in pages:
                ui.button(
                    page['label'],
                    icon=page.get('icon', 'broken_image'),
                    on_click=lambda uri=page['uri']: ui.navigate.to(uri)
                ).props('flat').classes('w-full justify-start')
    header = ui.header(elevated=True).style('display: flex; align-items: center;')
    with header: # background-color: #1976d2; color: white;
        ui.button(on_click=lambda: drawer.toggle(), icon='menu').style('width: 40px; height: 40px; padding: 0')# , color='white' # color: #ccc; 
        ui.label(settings.frontend.title).classes('text-h6 ml-2')
        ui.space()

        login_btn()

        with ui.row().classes('items-center'):
            # ui.button('Dark', on_click=dark.enable)
            # ui.button('Light', on_click=dark.disable)
            ui.icon('dark_mode').classes('mr-1')
            ui.switch().bind_value(darkmode)
    
    # with ui.column().classes('w-full h-screen'): # Header pushes this down
    with ui.column().classes('w-full items-center').style('height: calc(100vh - 124px); overflow: auto;'):
        page_func()
