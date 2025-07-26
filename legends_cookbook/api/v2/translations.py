from fastapi import APIRouter, Depends, HTTPException, Query, Response
from typing import Optional, List
from ...db import get_db, Session
from ...schemas.translation import TranslationModel, TranslationCreate, TranslationUpdate
from ...models.translation import Translation
from ...services.translations_svc import TranslationRepository
 

router = APIRouter()
repo = TranslationRepository()


@router.get("/", response_model=List[TranslationModel])
def list_entities(response: Response, db: Session = Depends(get_db), lang_short: str = Query(None), binding_label: str = Query(None), limit: int = Query(50), offset: int = Query(0)):
    if lang_short != None:
        count, result = repo.get_all_by_lang(db, lang=lang_short, skip=offset, limit=limit)
    elif binding_label != None:
        count, result = repo.get_all_by_binding_label(db, binding_label=binding_label, skip=offset, limit=limit)
    else:
        count, result = repo.get_all_paginated(db, skip=offset, limit=limit)
    if not result:
        if lang_short != None:
            raise HTTPException(status_code=200, detail=f"No Translations found for language {lang_short}.")
        elif binding_label != None:
            raise HTTPException(status_code=200, detail=f"No Translations found for binding label {binding_label}.")
        else:
            raise HTTPException(status_code=200, detail="No Translations found.")
    
    response.headers['x-item-count'] = str(count)
    return result

@router.get("/{translation_id}", response_model=TranslationModel)
def get_entity(response: Response, translation_id: int, db: Session = Depends(get_db)):
    result = repo.get(db, translation_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Translation not found by ID={translation_id}")
    return result

@router.get("/{language_id}/{binding_id}", response_model=TranslationModel)
def get_entity_by_language_id_and_binding_id(response: Response, language_id: int, binding_id: int, db: Session = Depends(get_db)):
    result = repo.get_by_lang_and_binding(db, lang_id=language_id, binding_id=binding_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Translation not found by language_id={language_id} and binding_id={binding_id}")
    return result

@router.post("/", response_model=TranslationModel)
def create_entity(dto: TranslationCreate, db: Session = Depends(get_db)):
    result = repo.create(db, obj_in=dto)
    return result

@router.put("/{translation_id}", response_model=TranslationModel)
def update_entity(translation_id: int, dto: TranslationUpdate, db: Session = Depends(get_db)):
    result = repo.update(db, translation_id=translation_id, obj_in=dto)
    return result

@router.delete("/{translation_id}", response_model=TranslationModel)
def delete_entity(translation_id: int, db: Session = Depends(get_db)):
    entity = repo.delete(db, translation_id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"Translation not found by ID={translation_id}")
    
    return entity
