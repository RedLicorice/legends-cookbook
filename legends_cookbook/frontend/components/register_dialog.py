from nicegui import ui, app, events
import logging

from ...services.users_svc import UsersService


with ui.dialog() as dialog, ui.card():
    ui.label('Are you sure?')

    with ui.label(text='Username or Email'):
        user = ui.input(value='some text').props('clearable')
    
    with ui.label(text='Password'):
        psw = ui.input(value='some text', password=True).props('clearable')
    
    with ui.row():
        ui.button('Yes', on_click=lambda: dialog.submit('Yes'))
        ui.button('No', on_click=lambda: dialog.submit('No'))

async def show():
    ui.notify(f'Dialog open')
    result = await dialog
    ui.notify(f'You chose {result}')

def component():
    ui.button('Register', on_click=show)