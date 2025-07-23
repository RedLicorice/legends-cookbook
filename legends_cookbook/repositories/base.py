from typing import TypeVar, Generic, Type, List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from sqlalchemy import func

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def max_id(self, db: Session) -> Union[int, None]:
        if not hasattr(self.model, 'id'):
            return None
        return db.query(func.max(self.model.id)).scalar()

    def count_all(self, db: Session) -> List[ModelType]:
        _query = db.query(self.model)
        count = _query.count()
        return count

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        _query = db.query(self.model).filter(self.model.id == id)
        result = _query.first()
        return result

    def get_all_paginated(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        _query = db.query(self.model)
        count = _query.count()
        result = _query.offset(skip).limit(limit).all()
        return count, result

    def get_all(self, db: Session) -> List[ModelType]:
        _query = db.query(self.model)
        count = _query.count()
        result = _query.all()
        return count, result
    
    def get_by_attr(self, db: Session, attr_name: str, attr_value) -> Optional[ModelType]:
        _query = db.query(self.model).filter(getattr(self.model, attr_name) == attr_value)
        result = _query.first()
        return result
    
    def get_all_by_attr(self, db: Session, attr_name: str, attr_value, skip: int = 0, limit: int = None) -> Optional[ModelType]:
        _query = db.query(self.model).filter(getattr(self.model, attr_name) == attr_value)
        if limit != None:
            _query = _query.offset(skip).limit(limit)
        
        count = _query.count()
        result = _query.all()
        return count, result

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        obj = self.model(**obj_in.dict())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def update(self, db: Session, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        obj_data = db_obj.__dict__
        update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> Optional[ModelType]:
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj