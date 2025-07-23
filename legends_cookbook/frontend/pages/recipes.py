from nicegui import ui, app, events
import logging
import hashlib

columns = [
    {'name': 'ingredient', 'label': 'Ingredient', 'field': 'ingredient', 'align': 'left', 'sortable': True},
    {'name': 'pct', 'label': 'Percentage', 'field': 'pct', 'sortable': True},
]
rows = [
    {'ingredient': 'THCa', 'pct': 75},
    {'ingredient': 'CBC', 'pct': 10},
    {'ingredient': 'HTFSE', 'pct': 10},
    {'ingredient': 'CDT', 'pct': 5}
]

def hash_color(name):
    hash = hashlib.md5(name.encode()).hexdigest()
    r = int(hash[:2], 16)
    g = int(hash[2:4], 16)
    b = int(hash[4:6], 16)
    return f'rgb({r},{g},{b})'



def page():
    with ui.card(align_items='center').tight().classes('flex flex-col p-2'):
        ui.label('[Recipe Name]').classes('text-h4')

        with ui.row():
            ui.table(columns=columns, rows=rows, row_key='name') \
                .classes('q-table--flat q-table--borderless bg-transparent')

            # chart = ui.highchart({
            #     'title': False,
            #     'chart': {'type': 'bar'},
            #     'xAxis': {'categories': [x['ingredient'] for x in rows]},
            #     'series': [{'name':x['ingredient'], 'data': [x['pct']]} for x in rows]
            # }).classes('h-64')
            color_map = [hash_color(row['ingredient']) for row in rows]

            ui.highchart({
                'title': False,
                'chart': {'type': 'bar'},
                'legend': {'enabled': False},
                'xAxis': {
                    'categories': [x['ingredient'] for x in rows],
                    'title': {'text': 'Ingredients'}
                },
                'yAxis': {
                    'title': {'text': 'Percentage'}
                },
                'series': [{
                    'name': 'Percentage',
                    'data': [{'y': row['pct'], 'color': color_map[i]} for i, row in enumerate(rows)]
                }]
            }).classes('h-64')