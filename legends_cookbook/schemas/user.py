from pydantic import BaseModel, EmailStr
from typing import Union, Optional, List
from datetime import datetime


class UserModel(BaseModel):
    id: int
    name: str
    telegram_user_id: str
    
    created: datetime
    last_updated: datetime

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    name: str
    telegram_user_id: str

class UserUpdate(UserCreate):
    id: int