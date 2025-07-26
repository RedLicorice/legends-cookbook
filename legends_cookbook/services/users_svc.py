from ..repositories.user import UserRepository
from ..schemas.user import UserModel, UserCreate, UserUpdate
from ..db import db_session, Session
from typing import Optional, List, Union
import logging
from io import StringIO

class UsersService:

    def __init__(self):
        self.repo = UserRepository()
    
    def get_users_count(self):
        with db_session() as db:
            return self.repo.count_all(db)
    
    def search_user(self, text: str, skip: Optional[int] = 0, limit: Optional[int] = None, as_dict: Optional[bool] = True):
        with db_session() as db:
            if text.startswith('#') and text.lstrip('#').isnumeric():
                telegram_id = int(text.lstrip('#'))
                logging.info(f'Search users by telegram_id: {telegram_id}')
                __data = self.repo.get_by_telegram_user_id(db, telegram_id=telegram_id)

                count = 1 if __data else 0
                data = [__data] if __data else []
            else:
                count, data = self.repo.search_by_name(db, text, skip=skip, limit=limit)
            
            _data = [UserModel.model_validate(x) for x in data]
            if as_dict:
                _data = [x.model_dump() for x in _data]

            return count, _data

    def get_user(self, id: int, as_dict: Optional[bool] = True):
        with db_session() as db:
            data = self.repo.get(db, id)
            
            _data = UserModel.model_validate(data)

            if as_dict:
                _data = _data.model_dump()

            return _data
    
    def get_users(self, skip: Optional[int] = 0, limit: Optional[int] = None, as_dict: Optional[bool] = True):
        with db_session() as db:
            if limit != None:
                count, data = self.repo.get_all_paginated(db, skip=skip, limit=limit)
            else:
                count, data = self.repo.get_all(db)
            
            _data = [UserModel.model_validate(x) for x in data]

            if as_dict:
                _data = [x.model_dump() for x in _data]

            return count, _data
    
    def get_free_id(self):
        with db_session() as db:
            return self.repo.max_id(db) + 1

    def upsert_user(self, name: str, telegram_id: str, id: Optional[int] = None):
        if id:
            _dto = UserUpdate(name=name, telegram_user_id=telegram_id, id=id)
        else:
            _dto = UserCreate(name=name, telegram_user_id=telegram_id)
        
        return self.upsert_user(_dto)
    
    def upsert_user(self, create: Union[UserCreate|UserUpdate]):
        with db_session() as db:
            if hasattr(create, 'id') and create.id != None:
                existing = self.repo.get(db, id=create.id)
            else:
                existing = self.repo.get_by_telegram_user_id(db, create.telegram_user_id)
            
            if not existing:
                orm_model = self.repo.create(db, create)
                logging.info(f"Created user Id: {orm_model.id}, TG ID: {orm_model.telegram_user_id}, Name: {orm_model.name}")
            else:
                orm_model = self.repo.update(db, existing, create)
                logging.info(f"Updated user Id: {orm_model.id}, TG ID: {orm_model.telegram_user_id}, Name: {orm_model.name}")
            
            model = UserModel.model_validate(orm_model)
            return model.model_dump()
    
    def delete_user(self, id: int):
        with db_session() as db:
            orm_model = self.repo.delete(db, id)
            logging.info(f"Deleted user Id: {id}, Name: {orm_model.name}")
            return UserModel.model_validate(orm_model)
    
    def delete_users(self, id_list: List[int]):
        with db_session() as db:
            result = {}
            for id in id_list:
                orm_model = self.repo.delete(db, id)
                result[id] = UserModel.model_validate(orm_model)
                logging.info(f"(Mass) Deleted user Id: {id}, Name: {orm_model.name}")
            return result
