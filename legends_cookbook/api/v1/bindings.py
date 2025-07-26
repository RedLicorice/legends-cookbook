from fastapi import APIRouter, Depends, HTTPException, Query, Response
from datetime import datetime
from typing import Optional, List, Union
from ...db import get_db, Session
from ...schemas.binding import BindingModel, BindingCreate, BindingUpdate
from ...models.binding import Binding
from ...repositories.binding import BindingRepository

router = APIRouter()
repo = BindingRepository()

@router.get("/", response_model=List[BindingModel])
def list_entities(response: Response, db: Session = Depends(get_db), limit: int = Query(50), offset: int = Query(0)):
    count, result = repo.get_all_paginated(db, skip=offset, limit=limit)
    response.headers['x-item-count'] = str(count)
    return result

@router.get("/{binding_id}", response_model=BindingModel)
def get_entity(binding_id: int, db: Session = Depends(get_db)):
    existing_entity = repo.get(db, id=binding_id)
    if not existing_entity:
        raise HTTPException(status_code=404, detail=f"Binding with id={binding_id} does not exist")
    return existing_entity

@router.post("/", response_model=BindingModel)
def create_entity(dto: BindingCreate, db: Session = Depends(get_db)):
    new_entity = repo.create(db, dto)
    return new_entity

@router.put("/{binding_id}", response_model=BindingModel)
def update_entity(binding_id: int, dto: BindingUpdate, db: Session = Depends(get_db)):
    _existing = repo.get(db, id=binding_id)
    entity = repo.update(db, db_obj=_existing, obj_in=dto)
    return entity

@router.delete("/{binding_id}", response_model=BindingModel)
def delete_entity(binding_id: str, db: Session = Depends(get_db)):
    entity = repo.delete(db, id=binding_id)
    return entity

@router.get("/by-label/{label}", response_model=BindingModel)
def get_entity_by_label(label: str, db: Session = Depends(get_db)):
    existing_entity = repo.get_by_label(db, label=label)
    if not existing_entity:
        raise HTTPException(status_code=404, detail="Entity with same label does not exist")
    return existing_entity

@router.put("/by-label/{label}", response_model=BindingModel)
def update_entity_by_label(label: str, dto: BindingUpdate, db: Session = Depends(get_db)):
    entity = repo.update_by_label(db, label=label, dto=dto)
    return entity

@router.delete("/by-label/{label}", response_model=BindingModel)
def delete_entity_by_label(label: str, db: Session = Depends(get_db)):
    entity = repo.delete_by_label(db, label)
    return entity

@router.get("/search/{label}", response_model=Union[List[BindingModel]|None])
def search_binding_by_label_like(label: str, response: Response, db: Session = Depends(get_db), limit: int = Query(None), offset: int = Query(0)):
    count, result = repo.search_by_label(db, label=label, skip=offset, limit=limit)

    response.headers['x-item-count'] = str(count)
    return result