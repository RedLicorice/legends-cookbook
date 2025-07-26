from fastapi import APIRouter, Depends, HTTPException, Query, Response
from datetime import datetime
from typing import Optional, List
from ...db import get_db, Session
from ...schemas.language import LanguageModel, LanguageCreate, LanguageUpdate
from ...repositories.language import LanguageRepository

router = APIRouter()
repo = LanguageRepository()

@router.get("/", response_model=List[LanguageModel])
def list_entities(response: Response, db: Session = Depends(get_db), limit: int = Query(50), offset: int = Query(0)):
    count, result = repo.get_all_paginated(db, skip=offset, limit=limit)

    response.headers['x-item-count'] = str(count)
    return result

@router.get("/{lang_short}", response_model=LanguageModel)
def get_entity(lang_short: str, db: Session = Depends(get_db)):
    existing_entity = repo.get_by_short_with_tl(db, short=lang_short)
    if not existing_entity:
        raise HTTPException(status_code=404, detail="Entity with specified short value does not exist")
    return existing_entity

@router.post("/", response_model=LanguageModel)
def create_entity(dto: LanguageCreate, db: Session = Depends(get_db)):
    new_entity = repo.create(db, obj_in=dto)
    return new_entity

@router.put("/{lang_short}", response_model=LanguageModel)
def update_entity(lang_short: str, entity_update: LanguageUpdate, db: Session = Depends(get_db)):
    entity = repo.update_by_short(db, short=lang_short, dto=entity_update)
    return entity

@router.delete("/{lang_short}", response_model=LanguageModel)
def delete_entity(lang_short: str, db: Session = Depends(get_db)):
    entity = repo.delete_by_short(db, short=lang_short)
    return entity