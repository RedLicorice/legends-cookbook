from sqlalchemy.orm import  Mapped, relationship, mapped_column
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, DateTime, ForeignKey, UniqueConstraint
from typing import Optional, List, TYPE_CHECKING
if TYPE_CHECKING:
    from .ingredient import Ingredient
    from .recipe import Recipe
from .base import Base


class RecipeIngredient(Base):
    __tablename__ = 'recipe_ingredients'
    id = mapped_column(Integer, primary_key=True, index=True)
    
    # Recipe Reference
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"))
    recipe: Mapped["Recipe"] = relationship(back_populates="ingredients")

    # Ingredient Reference
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"))
    ingredient: Mapped["Ingredient"] = relationship(back_populates="recipes")

    # Details
    pct = mapped_column(Integer)

    # Common
    created = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_updated = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())