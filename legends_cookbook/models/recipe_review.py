from sqlalchemy.orm import  Mapped, relationship, mapped_column
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, DateTime, ForeignKey, UniqueConstraint
from typing import Optional, List, TYPE_CHECKING
if TYPE_CHECKING:
    from .user import User
    from .recipe import Recipe
from .base import Base


class RecipeReview(Base):
    __tablename__ = 'recipe_reviews'
    id = mapped_column(Integer, primary_key=True, index=True)
    
    # Recipe Reference
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"))
    recipe: Mapped["Recipe"] = relationship(back_populates="reviews")

    # Comment Author
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="reviews")

    # Content
    rating = mapped_column(Integer, nullable=False)
    comment = mapped_column(String, nullable=True)

    # Common
    created = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_updated = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())