from ..models import User
from ..schemas.user import UserCreate, UserUpdate, UserModel
from .base import BaseRepository
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound, DuplicateColumnError
from typing import Optional, Union, List

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(User)

    def search_by_name(self, db: Session, label: str, skip: int = 0, limit: int = None) -> Union[List[User]|None]:
        search = "%{}%".format(label)
        query = db.query(User).filter(User.name.like(search))
        _count = query.count()
        if limit != None:
            query = query.offset(skip).limit(limit)
        return _count, query.all()

    def get_by_telegram_user_id(self, db: Session, telegram_id: str) -> User | None:
        result = super().get_by_attr(db, 'telegram_user_id', telegram_id)
        return result
    
    def create(self, db: Session, obj_in: UserCreate) -> User:
        _entity = self.get_by_telegram_user_id(db, telegram_id=obj_in.telegram_user_id)
        if _entity:
            raise DuplicateColumnError("Entity with same telegram_user_id already exists, use PUT to update.")
        result = super().create(db, obj_in)
        return result
    
    def update_by_telegram_user_id(self, db: Session, telegram_id: str, dto: UserUpdate) -> User:
        # result = db.query(Binding).filter(Binding.label == label).first()
        _entity = self.get_by_telegram_user_id(db, telegram_id=telegram_id)
        result = super().update(db, _entity, dto)
        return result

    def delete_by_telegram_user_id(self, db: Session, telegram_id: str) -> User | None:
        _entity = self.get_by_telegram_user_id(db, telegram_id=telegram_id)
        result = super().delete(db, _entity.id)
        return result