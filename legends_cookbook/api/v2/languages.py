from fastapi import APIRouter, Depends, HTTPException, Query, Response
from datetime import datetime
from typing import Optional, List
from ...db import get_db, Session
from ...schemas.language import LanguageModel, LanguageCreate, LanguageUpdate
from ...services.languages_svc import LanguagesService

router = APIRouter()
svc = LanguagesService()

@router.get("/", response_model=List[LanguageModel])
def list_entities(response: Response, limit: int = Query(50), offset: int = Query(0)):
    count, result = svc.get_languages(skip=offset, limit=limit, as_dict=False)
    response.headers['x-item-count'] = str(count)
    return result

@router.get("/{lang_short}", response_model=LanguageModel)
def get_entity(lang_short: str):
    existing_entity = svc.get_language_by_short_with_tl(short=lang_short)
    if not existing_entity:
        raise HTTPException(status_code=404, detail="Entity with specified short value does not exist")
    return existing_entity

@router.post("/", response_model=LanguageModel)
def create_entity(dto: LanguageCreate):
    new_entity = svc.upsert_language(dto)
    return new_entity

@router.put("/{lang_short}", response_model=LanguageModel)
def update_entity(lang_short: str, entity_update: LanguageUpdate):
    entity = svc.upsert_language(entity_update)
    return entity

@router.delete("/{lang_short}", response_model=LanguageModel)
def delete_entity(lang_short: str):
    entity = svc.delete_by_short(lang_short)
    return entity