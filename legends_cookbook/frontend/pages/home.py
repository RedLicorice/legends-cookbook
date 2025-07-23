from nicegui import ui
from ...config import settings

from ...services.users_svc import UsersService
import logging

def top_recipes_table():
    columns = [
        {'name': 'name', 'label': 'Name', 'field': 'name', 'required': True, 'align': 'left'},
        {'name': 'author', 'label': 'Author', 'field': 'author'},
        {'name': 'likes', 'label': 'Likes', 'field': 'likes', 'sortable': True},
    ]
    rows = [
        {'name': 'THCa Blend', 'author': 'THCaSnow', 'likes': 10},
        {'name': 'HHC Blend', 'author': 'MrLucifer', 'likes': 9},
        {'name': 'Trippy Blend 1', 'author': 'Santa Claus', 'likes': 1},
        {'name': 'Trippy Blend 2', 'author': 'Santa Claus', 'likes': 0},
    ]
    ui.table(columns=columns, rows=rows, row_key='name')

def page():
    top_recipes_table()