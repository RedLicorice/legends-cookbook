from nicegui import ui, app, events
import logging

from ...services.users_svc import UsersService
from ...services.login_svc import LoginService
from ...config import settings

svc_login = LoginService()

def login_register_dialog():
    with ui.dialog() as dialog, ui.card():
        
        ui.markdown(content="We use Telegram for authentication.\nOur Butler bot will be happy to help you!")

        with ui.link(target=svc_login.generate_bot_login_link()):
            ui.button('Go to bot!', icon='person')

        return dialog

def user_profile_dialog():
    with ui.dialog() as dialog, ui.card():
        ui.label('Are you sure?')

        with ui.label(text='Username or Email'):
            user = ui.input(value='some text').props('clearable')
        
        with ui.label(text='Password'):
            psw = ui.input(value='some text', password=True).props('clearable')
        
        with ui.row():
            ui.button('Yes', on_click=lambda: dialog.submit('Yes'))
            ui.button('No', on_click=lambda: dialog.submit('No'))
        
        return dialog

async def show(dialog):
    ui.notify(f'Dialog open')
    result = await dialog
    ui.notify(f'You chose {result}')

def component():
    _diag = login_register_dialog()
    
    # If not logged in, show a button
    ui.button(icon='account_box', on_click=lambda x=_diag: show(x))\
        .props(f'color="secondary"')