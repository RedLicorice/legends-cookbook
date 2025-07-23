from pydantic import BaseModel, EmailStr
from typing import Union, Optional, List
from datetime import datetime


class RecipeModel(BaseModel):
    id: int
    name: str
    author_id: str
    
    created: datetime
    last_updated: datetime

    class Config:
        from_attributes = True

class RecipeCreate(BaseModel):
    name: str
    author_id: str

class RecipeUpdate(RecipeCreate):
    id: int