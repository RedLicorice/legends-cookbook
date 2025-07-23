from sqlalchemy.orm import  Mapped, relationship, mapped_column
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, DateTime, ForeignKey, UniqueConstraint
from typing import Optional, List, TYPE_CHECKING
if TYPE_CHECKING:
    from .user import User
    from .recipe_ingredient import RecipeIngredient
from .base import Base


class Recipe(Base):
    __tablename__ = 'recipes'
    id = mapped_column(Integer, primary_key=True, index=True)
    
    # Recipe Title
    name = mapped_column(String, index=True)

    # Recipe Author
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="recipes")

    # Ingredients
    ingredients: Mapped[List["RecipeIngredient"]] = relationship(back_populates="recipe")

    # Common
    created = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_updated = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())