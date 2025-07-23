from nicegui import ui, app, events, binding
import logging
from ...services.translations_svc import TranslationsService, TranslationModel
from ...services.languages_svc import LanguagesService, LanguageModel
from typing import Union, Optional, List
from pydantic import BaseModel


svc = TranslationsService()
lang_svc = LanguagesService()
grid = None
upload_dialog = None
table_column_definition = [
    {
        'headerName': 'ID',
        'field': 'id',
        'filter': 'agNumberColumnFilter',
        'floatingFilter': True,
        'sortable': True,
        'minWidth': 40,
        'maxWidth': 100,
        'hide': True,
    },
    {
        'headerName': 'Binding ID',
        'field': 'binding.id',
        'filter': 'agNumberColumnFilter',
        'floatingFilter': True,
        'sortable': True,
        'minWidth': 40,
        'maxWidth': 100
    },
    {
        'headerName': 'Binding Label',
        'field': 'binding.label',
        'filter': 'agTextColumnFilter',
        'floatingFilter': True,
        'editable': True,
        'sortable': True,
        'flex': 1,
    },
    {
        'headerName': 'Language',
        'field': 'language',
        'valueGetter': 'data.language.label + " (" + data.language.short.toUpperCase() + ")"', # JS not python
        'filter': 'agTextColumnFilter',
        'floatingFilter': True,
        'editable': False,
        'sortable': True,
        'minWidth': 40,
        'maxWidth': 100
    },
    {
        'headerName': 'Text',
        'field': 'text',
        'filter': 'agTextColumnFilter',
        'floatingFilter': True,
        'editable': True,
        'sortable': True,
        'flex': 1
    },
]

DEFAULT_LABEL_ENC = 'euc-kr'
DEFAULT_TEXT_ENC = 'iso-8859-1'

@binding.bindable_dataclass
class ImportLocaleStringParams:
    lang: str = None
    type: str = 'kor'
    label_encoding: str = DEFAULT_LABEL_ENC
    text_encoding: str = DEFAULT_TEXT_ENC
    content: Optional[bytes] = None

@ui.refreshable
def paginated_table(selected_lang: Optional[str] = None):
    global grid, table_column_definition

    current_page, set_current_page = ui.state(1) # Setter used by paginator
    per_page, set_per_page = ui.state(50) # Setter used by select
    total_pages, set_total_pages = ui.state(5) # Setter used by load_data
    show_data, set_show_data = ui.state([]) # Getter used by table, Setter used by load_data
    total_rows, set_total_rows = ui.state(0)

    search_term, set_search_term = ui.state("")
    pending_rows, set_pending_rows = ui.state({})

    current_language, set_current_language = ui.state("" if selected_lang is not None else selected_lang) # Setter used by select

    def load_data():
        skip = (current_page - 1) * per_page
        limit = per_page

        if search_term:
            count, rows = svc.search_translation(search_term, skip=skip, limit=limit)
        else:
            if current_language and current_language != "":
                count, rows = svc.get_translations(language_short=current_language, skip=skip, limit=limit)
            else:
                count, rows = svc.get_translations(skip=skip, limit=limit)
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

            _model = {'id': _id, 'label': f'NEW_LABEL_{len(pending_rows)+1}', 'text': ''}
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
        res = svc.delete_translations(not_pending)
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
        res = svc.upsert_translation_args(label=new_row['label'], text=new_row['text'], id=new_row['id'] if new_row['id'] != 0 else None)
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
        search_field = ui.input(label='Type to search Labels, start with "#" to search by ID', value=search_term, on_change=lambda e: handle_search(e.value)) \
            .props('autofocus outlined item-aligned input-class="ml-3" clearable') \
            .classes('w-2/3 self-center transition-all')

    # Manipulate data and filters block
    with ui.row().classes('w-full flex flex-row items-center justify-start'):
        # Language selection
        count, languages = lang_svc.get_languages()
        _options = [("Clear Filter", None)] + [(f"{l['label']} ({l['short'].upper()})", l['short']) for l in languages]
        def on_filter_language(v):
            if v:
                ui.notify(f'Selected language {v.upper()}')
            else:
                ui.notify('Cleared language selection')
            
            set_current_language(v)
        
        with ui.dropdown_button(text=f'Language Filter' if not current_language else f'Language = {current_language.upper()}', auto_close=True):
            for _text, _val in _options:
                ui.item(_text, on_click=lambda v=_val: on_filter_language(v))

        # Add / Delete Selection
        ui.button(icon='add', text='Add New', on_click=add_row)
        ui.button(icon='delete', text='Delete Selected', on_click=delete_selected)

        # Import *.txt
        with ui.dropdown_button(icon='upload', text=f'Import..', auto_close=True):
            ui.item(text='Import locale_string.txt', on_click=upload_dialog.open)
        
        # Export *.txt
        with ui.dropdown_button(icon='download', text=f'Export..', auto_close=True):
            ui.item(text='Export original locale_string.txt', on_click=upload_dialog.open)
            ui.item(text='Export bound locale_string.txt', on_click=upload_dialog.open)
            ui.item(text='Export client locale_string.txt', on_click=upload_dialog.open)
            ui.item(text='Export *.po', on_click=upload_dialog.open)
        
        # Hide Column
        with ui.element().classes('ml-auto'):
            ui.switch(text='Hide row ID', value=True, on_change=lambda x: grid.run_grid_method('setColumnsVisible', ['id'], not x.value))
            ui.switch(text='Hide Language', value=(current_language != None and current_language != ""), on_change=lambda x: grid.run_grid_method('setColumnsVisible', ['language'], not x.value))
            ui.switch(text='Hide Binding Label', on_change=lambda x: grid.run_grid_method('setColumnsVisible', ['binding.label'], not x.value))
    
    # Lil hack to hide language column when a language is selected
    table_column_definition[3]['hide'] = (current_language != None and current_language != "")

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

def page(selected_lang: Optional[str] = None):
    global upload_dialog
    with ui.dialog() as upload_dialog , ui.card().classes('w-2/3'):
        parameters = ImportLocaleStringParams()

        ui.label('Upload locale_string.txt').classes('text-h5')
        with ui.expansion('Info', icon='help').classes('w-full'):
            ui.markdown(content="""
                Upload a standard locale_string_<LANG>.txt file or a client locale_string file.
                
                A standard locale_string file is a text (.txt) file in the format:
                
                `"LABEL";\\n
                    "TEXT";\\n\\n`
                
                A client locale_string file is a text (.txt) file in the format:
                `ID\\t"TEXT"\\n`
                
                Where:
                        
                - <LANG> is the language you should be importing
                - LABEL is the text value passed to LC_TEXT in the original source code. 
                    - Normally that's the former korean locale.
                    - This value is used to identify the bindings the imported translation will refer to.
                - ID is the binding, corresponding to the Label in client-side locale
                - TEXT is the translation value, that will be imported for the selected language
            
                **Encoding for this file will eventually be decoded and converted to utf-8.
                There are checks in place to avoid mojibake.**
            """)

        with ui.column().classes('w-full'):
            with ui.column().classes('w-full'):
                ui.label('What language are you uploading?')
                count, languages = lang_svc.get_languages()
                _options = {l['short']: f"{l['label']} ({l['short'].upper()})" for l in languages}
                sel_lang = ui.select(_options, label=f'Language').classes('w-64')
                sel_lang.bind_value(parameters, 'lang')
            
            with ui.column().classes('w-full') as format_row:
                def on_change_format(value):
                    if value == 'kor':
                        label_enc.value=DEFAULT_LABEL_ENC
                        text_enc.value=DEFAULT_TEXT_ENC
                    elif value == 'client':
                        label_enc.value = 'utf-8'
                        text_enc.value = DEFAULT_TEXT_ENC
                    else:
                        label_enc.value = 'utf-8'
                        text_enc.value = 'utf-8'
                ui.label('What format is adopted for this file\'s labels?')
                file_type = ui.toggle(
                    {'kor':'Binding Text (Korean)', 'binding':'Binding Label', 'client':'Binding ID (Client)'}, 
                    value='kor',
                    on_change=lambda e: on_change_format(e.value)
                )
                file_type.bind_value(
                    parameters, 
                    'type'
                )

            with ui.column().classes('w-full') as encoding_row:
                with ui.column() as label_enc_row:
                    ui.label('What encoding is adopted for this file\'s labels?')
                    label_enc = ui.input(value=DEFAULT_LABEL_ENC)
                    label_enc.bind_value(parameters, 'label_encoding')

                ui.label('What encoding is adopted for this file\'s texts?')
                text_enc = ui.input(value=DEFAULT_TEXT_ENC)
                text_enc.bind_value(parameters, 'text_encoding')
            
            with ui.column().classes('w-full') as encoding_row_utf8:
                ui.label('The file will be treated as utf-8')
            
            encoding_row.bind_visibility_from(file_type, 'value', lambda val: val in ['kor', 'client'])
            label_enc_row.bind_visibility_from(file_type, 'value', lambda val: val in ['kor'])
            encoding_row_utf8.bind_visibility_from(file_type, 'value', lambda val: val in ['binding'])
            
            with ui.column().classes('w-full'):
                async def handle_upload(e: events.UploadEventArguments):
                    parameters.content = e.content.read()
                    ui.notify(f'Uploaded {e.name}, {len(parameters.content)} bytes')
                
                ui.label('Select and upload the file, when the upload is complete the translations will be available.')
                upload = ui.upload(
                    on_upload=lambda e: handle_upload(e),
                    on_rejected=lambda: ui.notify('Rejected!'),
                    max_file_size=1_000_000,
                    auto_upload=True,
                ).props('accept=.txt').classes('w-full max-w-full')
            
        async def on_btn_import(e):
            if not parameters.lang:
                ui.notify("Please select language")
                return
            
            if parameters.type in ['kor', 'binding']:
                results = svc.import_locale_string(
                    lang = parameters.lang,
                    content=parameters.content,
                    bound=parameters.type == 'binding',
                    label_encoding=parameters.label_encoding,
                    text_encoding=parameters.text_encoding
                )
            else:
                results = svc.import_client_locale_string(
                    lang = parameters.lang,
                    content=parameters.content,
                    text_encoding=parameters.text_encoding)
            ui.notify(f'Imported {len(results)} translations for language "{parameters.lang.upper()}"')
            paginated_table.refresh()
        
        with ui.row().classes('w-full flex flex-row items-end justify-end'):
            ui.button('Close', on_click=upload_dialog.close)
            import_btn = ui.button('Import!', on_click=on_btn_import)
            
    
    with ui.card().classes('w-full flex-1 flex flex-col'):
        ui.label('Translations').classes('text-h4')
        paginated_table(selected_lang)
