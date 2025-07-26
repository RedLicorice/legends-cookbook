from pydantic import BaseModel, EmailStr
from typing import Union, Optional, List
from datetime import datetime


class LoginTokenModel(BaseModel):
    id: int
    telegram_user_id: int

    token: str
    expires: datetime
    used: bool
    active: bool
    
    created: datetime
    last_updated: datetime

    class Config:
        from_attributes = True

class LoginTokenCreate(BaseModel):
    telegram_user_id: str
    name: Optional[str] = None
    token: Optional[str] = None
    expires: Optional[datetime] = None
    used: Optional[bool] = False
    active: Optional[bool] = False

class LoginTokenUpdate(LoginTokenCreate):
    id: int