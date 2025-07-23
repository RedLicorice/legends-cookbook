from nicegui import ui, app, events
import logging
from ...services.languages_svc import LanguagesService

svc = LanguagesService()
grid = None

table_column_definition = [
    {
        'headerName': 'ID',
        'field': 'id',
        'filter': 'agNumberColumnFilter',
        'floatingFilter': True,
        'sortable': True,
        'minWidth': 50
    },
    {
        'headerName': 'Flag',
        'field': 'flag',
        'editable': True,
        'sortable': True,
        'minWidth': 1
    },
    {
        'headerName': 'Short',
        'field': 'short',
        'filter': 'agTextColumnFilter',
        'floatingFilter': True,
        'editable': True,
        'sortable': True
    },
    {
        'headerName': 'Label',
        'field': 'label',
        'filter': 'agTextColumnFilter',
        'floatingFilter': True,
        'flex': 1,
        'editable': True,
        'sortable': True
    }
]

@ui.refreshable
def paginated_table():
    global grid, table_column_definition

    current_page, set_current_page = ui.state(1) # Setter used by paginator
    per_page, set_per_page = ui.state(50) # Setter used by select
    total_pages, set_total_pages = ui.state(5) # Setter used by load_data
    show_data, set_show_data = ui.state([]) # Getter used by table, Setter used by load_data
    total_rows, set_total_rows = ui.state(0)

    search_term, set_search_term = ui.state("")
    pending_rows, set_pending_rows = ui.state({})

    def load_data():
        skip = (current_page - 1) * per_page
        limit = per_page

        if search_term:
            count, rows = svc.search_language(search_term, skip=skip, limit=limit)
        else:
            count, rows = svc.get_languages(skip=skip, limit=limit)
        _total_pages = max(1, (count + per_page - 1) // per_page)
        
        set_show_data(rows)
        set_total_pages(_total_pages)
        set_total_rows(count)

    def pagination():
        # Scrolling window logic for pagination start/end buttons
        _count = 5
        if current_page <= 3:
            start_from = 1
        else:
            if current_page + 2 > total_pages:
                start_from = total_pages - _count + 1
            else:
                start_from = current_page - 2
        if start_from < 0:
                start_from = 1
        
        if current_page <= 3:
            end_to = total_pages if total_pages < _count else _count
        else:
            end_to = current_page + 2
            if end_to > total_pages:
                end_to = total_pages
        
        
        pagination = ui.pagination(start_from, end_to, value=current_page, direction_links=True)
        pagination.on_value_change(lambda e: set_current_page(e.value))
        return pagination

    def get_new_id():
        _new_id = svc.get_free_id()
        _pending_count = len(pending_rows)
        return _new_id + _pending_count
    
    def focus_on_new_row(row_index: int):
        grid.run_grid_method('ensureIndexVisible', row_index)
        grid.run_grid_method('startEditingCell', {
            'rowIndex': row_index,
            'colKey': 'label',
        })

    def add_row():
        def _add_row():
            _id = get_new_id()
            assert _id not in pending_rows

            _model = {'id': _id, 'label': f'NEW_LANGUAGE_{len(pending_rows)+1}', 'short': f'N{len(pending_rows)+1}', 'flag': '🏳️'}
            show_data.append(_model)

            pending_rows[_id] = _model

            ui.notify(f'Added row with ID {_id}, update it to save.')

            grid.update()

            # Attendi un frame per assicurarti che il grid sia aggiornato
            ui.timer(0.1, lambda: focus_on_new_row(len(show_data) - 1), once=True)
        
        if current_page == total_pages:
            _add_row()
        else:
            set_current_page(total_pages)
            ui.notify('Click again to add a new row!')
    
    async def delete_selected():
        selected_id = [row['id'] for row in await grid.get_selected_rows()]
        if not selected_id:
            return
        not_pending = [id for id in selected_id if not id in pending_rows]
        res = svc.delete_languages(not_pending)
        res_id = [k for k,v in res.items()]

        deleted_pending = [id for id in selected_id if id in pending_rows]
        for k in deleted_pending:
            pending_rows.pop(k, None)

        _deleted_ids = res_id+deleted_pending
        show_data[:] = [row for row in show_data if row['id'] not in _deleted_ids]
        
        ui.notify(f'Deleted row with ID {selected_id}')
        grid.update()
    
    def handle_cell_value_change(e):
        new_row = e.args['data']
        res = svc.upsert_language_args(label=new_row['label'], short=new_row['short'], flag=new_row['flag'], id=new_row['id'] if new_row['id'] != 0 else None)
        del pending_rows[res['id']]
        ui.notify(f'Updated row to: {res}')
        show_data[:] = [row | res if row['label'] == res['label'] else row for row in show_data]
    
    def handle_search(value) -> None:
        if not value:
            search = ""
        else:
            search = value
        set_search_term(search)
    
    # Top Pagination block
    with ui.row().classes('w-full flex flex-row items-center justify-start'):
        _opts = [(f'{x}/page', x) for x in [10, 30, 50, 100, 250]]
        _opts.append((f'All ({total_rows})', total_rows))
        with ui.dropdown_button(text=f'{per_page}/page', auto_close=True):
            for _text, _val in _opts:
                ui.item(_text, on_click=lambda v=_val: set_per_page(v))
        ui.button(icon='fast_rewind', text='First/1', on_click=lambda e: set_current_page(1)) # '1 ⏮'
        ui.number(value=current_page, on_change=lambda e: set_current_page(e.value), min=1, max=total_pages)\
            .props('outlined item-aligned input-class="ml-3"') \
            .classes('w-32 self-center transition-all')
        ui.button(icon='fast_forward', text=f'Last/{total_pages}', on_click=lambda e: set_current_page(total_pages)) # f'⏭ {total_pages}'
        ui.button(icon='refresh', text='Refresh', on_click=lambda e: paginated_table.refresh()) # '1 ⏮'
    
    # Big search block
    with ui.row().classes('w-full flex flex-row items-center justify-center'):
        search_field = ui.input(label='Type to search Labels or Short, start with "#" to search by ID', value=search_term, on_change=lambda e: handle_search(e.value)) \
            .props('autofocus outlined item-aligned input-class="ml-3" clearable') \
            .classes('w-2/3 self-center transition-all')

    # Manipulate data and filters block
    with ui.row().classes('w-full flex flex-row items-center justify-start'):
        ui.button(icon='add', text='Add New', on_click=add_row)
        ui.button(icon='delete', text='Delete Selected', on_click=delete_selected)
    
    # The grid itself
    grid = ui.aggrid({
        'columnDefs': table_column_definition,
        'rowData': show_data,
        'rowSelection': 'multiple',
        'stopEditingWhenCellsLoseFocus': True,
    }, auto_size_columns=False)
    grid.on('cellValueChanged', handle_cell_value_change)
    grid.classes('flex-1 min-h-100')

    # with ui.element().classes('ml-auto'):
    with ui.row().classes('w-full flex-row items-end justify-end'):
        pagination()
    ui.separator()
    with ui.row().classes('w-full flex-row items-center justify-center'):
        ui.label(text=f'Page {current_page} of {total_pages}; {total_rows} total rows.')
    
    load_data()

def handle_dark_mode(is_dark_mode):
    grid.classes(
        add='ag-theme-balham-dark' if is_dark_mode else 'ag-theme-balham',
        remove='ag-theme-balham ag-theme-balham-dark'
    )

def page():
    with ui.card().classes('w-full flex-1 flex flex-col'):
        ui.label('Languages').classes('text-h4')
        paginated_table()
