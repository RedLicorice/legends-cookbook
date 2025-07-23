from sqlalchemy.orm import  Mapped, relationship, mapped_column
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, DateTime
from typing import Optional, List, TYPE_CHECKING
from .base import Base
if TYPE_CHECKING:
    from .recipe_review import RecipeReview
    from .recipe import Recipe

class User(Base):
    __tablename__ = 'users'
    id = mapped_column(Integer, primary_key=True, index=True)

    # Telegram Info
    name = mapped_column(String, unique=True, index=True)
    telegram_user_id = mapped_column(String, unique=True, index=True)
    
    # User's recipes
    recipes: Mapped[List["Recipe"]] = relationship(back_populates="author")

    # User's reviews
    reviews: Mapped[List["RecipeReview"]] = relationship(back_populates="author")

    # Common
    created = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_updated = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())