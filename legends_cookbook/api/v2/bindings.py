from fastapi import APIRouter, Depends, HTTPException, Query, Response, UploadFile
from fastapi.responses import StreamingResponse
from datetime import datetime
from typing import Optional, List, Union
from ...services.bindings_svc import BindingService, BindingModel, BindingCreate, BindingUpdate

router = APIRouter()
svc = BindingService()

@router.get("/", response_model=List[BindingModel])
def list_entities(response: Response, limit: int = Query(50), offset: int = Query(0)):
    count, result = svc.get_bindings(skip=offset, limit=limit)
    response.headers['x-item-count'] = str(count)
    return result

@router.get("/{binding_id}", response_model=BindingModel)
def get_entity(binding_id: int):
    existing_entity = svc.get_binding(binding_id)
    if not existing_entity:
        raise HTTPException(status_code=404, detail=f"Binding with id={binding_id} does not exist")
    return existing_entity

@router.post("/", response_model=BindingModel)
def create_entity(dto: BindingCreate):
    new_entity = svc.upsert_binding(dto)
    return new_entity

@router.put("/{binding_id}", response_model=BindingModel)
def update_entity(binding_id: int, dto: BindingUpdate):
    if dto.id != binding_id:
        raise HTTPException(status_code=403, detail="Path binding_id and dto.id must match!")
    new_entity = svc.upsert_binding(dto)
    return new_entity

@router.delete("/{binding_id}", response_model=BindingModel)
def delete_entity(binding_id: str):
    entity = svc.delete_binding(binding_id)
    return entity

@router.get("/search/{label}", response_model=Union[List[BindingModel]|None])
def search_binding_by_label_like(label: str, response: Response, limit: int = Query(None), offset: int = Query(0)):
    count, result = svc.search_binding(label=label, skip=offset, limit=limit)

    response.headers['x-item-count'] = str(count)
    return result

@router.post("/import", response_model=List[BindingModel])
async def import_locale_bindings(file: UploadFile):
    textdata = await file.read()
    bindings_dict = svc.convert_bindings_txt_to_dict(textdata=textdata)
    results = svc.import_bindings_dict(bindings_dict)
    return results

@router.get("/export")
async def export_locale_bindings():
    result = svc.export_bindings_txt()
    #Return result as file
    headers = {
        "Content-Disposition": f'attachment; filename="locale_bindings.txt"'
    }
    return StreamingResponse(result, media_type="text/plain", headers=headers)