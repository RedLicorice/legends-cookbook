from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile
from fastapi.responses import PlainTextResponse, FileResponse, StreamingResponse
from datetime import datetime
from typing import Optional, List
from ...db import get_db, Session
from ...schemas.binding import BindingModel
from ...schemas.translation import TranslationModel
from ...models.binding import Binding
from ...models.language import Language
from ...models.translation import Translation
from ...services.utils import get_str_tst
from ...services.locale_file_utils import convert_locale_string, load_locale_string, make_binding_tag
from io import StringIO
import logging

router = APIRouter()

@router.post("/import-locale-bindings", response_model=List[BindingModel])
async def import_locale_bindings(file: UploadFile, db: Session = Depends(get_db)):
    textdata = await file.read()

    # Bindings file MUST be in UTF-8
    content = textdata.decode("utf-8")
    bindings_dict = load_locale_string(content, strip=True, return_dict=True)

    # Bindings file maps text-to-label so we need to invert it
    # This also means duplicate labels will be overwritten.
    bindings_dict = {label:text for text,label in bindings_dict.items()} 

    results = []
    for label, text in bindings_dict.items(): 
        existing_entity = db.query(Binding).filter(Binding.label == label).first()
        if existing_entity:
            continue

        new_entity = Binding(
            label=label,
            text=text
        )
        db.add(new_entity)
        results.append(new_entity)
    db.commit()

    return results

@router.post("/import-locale-string/{lang_short}", response_model=List[TranslationModel])
async def import_locale_string(
        lang_short: str, 
        file: UploadFile, 
        label_encoding: str = Query("euc-kr"),
        text_encoding: str = Query("iso-8859-1"),
        db: Session = Depends(get_db)
    ):
    language = db.query(Language).filter(Language.short == lang_short).first()
    if not language:
        raise HTTPException(status_code=404, detail="Language not found.")

    content = await file.read()

    # content = textdata.decode("utf-8")
    logs, converted_text = convert_locale_string(
        content,
        label_encoding=label_encoding,
        text_encoding=text_encoding,
        lang_hint=lang_short
    )
    logging.debug(f"Converted file to {len(converted_text)} bytes \n LOGS: \n {logs}")

    locale_dict = load_locale_string(converted_text, strip=True, return_dict=True)

    results = []
    for label, text in locale_dict.items():
        binding = db.query(Binding).filter(Binding.text == label).first()
        if not binding:
            # We don't have this string bound so just ignore
            continue
        
        entity = db.query(Translation).filter(
                Translation.binding_id == binding.id, 
                Translation.language_id == language.id
            ).first()
        if not entity:
            new_entity = Translation(
                binding_id=binding.id,
                language_id=language.id,
                text=text
            )
            db.add(new_entity)
            results.append(new_entity)
        else:
            entity.text = text
            results.append(entity)
    
    db.commit()

    return results

@router.post("/import-bound-locale-string/{lang_short}", response_model=List[TranslationModel])
async def import_bound_locale_string(lang_short: str, file: UploadFile, db: Session = Depends(get_db)):
    language = db.query(Language).filter(Language.short == lang_short).first()
    if not language:
        raise HTTPException(status_code=404, detail="Language not found.")

    textdata = await file.read()
    content = textdata.decode("utf-8")
    locale_dict = load_locale_string(content, strip=True, return_dict=True)

    results = []
    for label, text in locale_dict.items():
        binding = db.query(Binding).filter(Binding.label == label).first()
        if not binding:
            # We don't have this string bound so just ignore
            continue
        
        new_entity = Translation(
            binding=binding.id,
            lang=language.short,
            text=text
        )
        db.add(new_entity)
        results.append(new_entity)
    
    db.commit()

    return results

@router.get("/export-locale-string/{lang_short}")
async def export_locale_string(lang_short: str, db: Session = Depends(get_db)):
    language = db.query(Language).filter(Language.short == lang_short).first()
    if not language:
        raise HTTPException(status_code=404, detail="Language not found.")

    _result = db.query(Binding,Translation) \
                        .filter(Translation.lang == lang_short) \
                        .filter(Binding.id == Translation.binding) \
                        .all()

    result = StringIO()
    for binding, translation in _result:
        result.write(f'"{binding.label}";\n')
        result.write(f'"{translation.text}";\n\n')
    result.seek(0)

    #Return result as file
    headers = {
        "Content-Disposition": f'attachment; filename="locale_string_{lang_short}.txt"'
    }
    return StreamingResponse(result, media_type="text/plain", headers=headers)

@router.get("/export-mali-locale-string/")
async def export_mali_locale_string(db: Session = Depends(get_db)):
    _result = db.query(Binding).all()
    
    result = StringIO()
    for binding in _result:
        token = make_binding_tag('LC', binding.id, binding.label)
        result.write(f'"{binding.label}";\n')
        result.write(f'"{token}";\n\n')
    result.seek(0)

    #Return result as file
    headers = {
        "Content-Disposition": 'attachment; filename="locale_string.txt"'
    }
    return StreamingResponse(result, media_type="text/plain", headers=headers)

@router.get("/export-mali-client-locale-string/{lang_short}")
async def export_mali_client_locale_string(lang_short: str, db: Session = Depends(get_db)):
    language = db.query(Language).filter(Language.short == lang_short).first()
    if not language:
        raise HTTPException(status_code=404, detail="Language not found.")

    _result = db.query(Binding,Translation) \
                        .filter(Translation.lang == lang_short) \
                        .filter(Binding.id == Translation.binding) \
                        .all()

    result = StringIO()
    for binding, translation in _result:
        result.write(f'{binding.id}\t{translation.text}\n')
    result.seek(0)

    #Return result as file
    headers = {
        "Content-Disposition": f'attachment; filename="{lang_short}__locale_string.txt"'
    }
    return StreamingResponse(result, media_type="text/plain", headers=headers)