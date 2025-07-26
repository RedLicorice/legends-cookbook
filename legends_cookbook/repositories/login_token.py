from ..models import LoginToken
from ..schemas.login_token import LoginTokenCreate, LoginTokenUpdate, LoginTokenModel
from .base import BaseRepository
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound, DuplicateColumnError
from typing import Optional, Union, List

class LoginTokenRepository(BaseRepository[LoginToken, LoginTokenCreate, LoginTokenUpdate]):
    def __init__(self):
        super().__init__(LoginToken)
    
    def get_by_token(self, db: Session, token: str) -> LoginToken | None:
        result = super().get_by_attr(db, 'token', token)
        return result

    def get_by_telegram_user_id(self, db: Session, telegram_id: str) -> LoginToken | None:
        result = super().get_by_attr(db, 'telegram_user_id', telegram_id)
        return result