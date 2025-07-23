from sqlalchemy.orm import  Session, Mapped, relationship, mapped_column
from sqlalchemy.sql import func
from sqlalchemy import or_, and_, Integer, String, DateTime, Boolean
import json
from typing import Optional, List, TYPE_CHECKING
if TYPE_CHECKING:
    from .recipe_ingredient import RecipeIngredient
from .base import Base
import logging


class Ingredient(Base):
    __tablename__ = 'ingredients'
    id = mapped_column(Integer, primary_key=True, index=True)
    name = mapped_column(String, unique=True)
    short = mapped_column(String, unique=True, index=True)

    # Ingredient information
    type = mapped_column(String) # Cannabinoid, Terpene
    origin = mapped_column(String) # Natural, Synthetic, Semi-Synthetic
    role = mapped_column(String) # Base, Booster, 
    min_pct = mapped_column(Integer)
    max_pct = mapped_column(Integer)
    typical_pct = mapped_column(Integer)
    yield_pct = mapped_column(Integer)
    active = mapped_column(Boolean)

    # Related recipes
    recipes: Mapped[List["RecipeIngredient"]] = relationship(back_populates="ingredient")

    # Common
    created = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_updated = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    @property
    def translation_count(self) -> int:
        return len(self.translations)

def init_table(SessionLocal):
    db: Session = SessionLocal()
    
    with open('bootstrap/ingredient.json', 'r') as f:
        ingredients_list = json.load(f)
        for item in ingredients_list:
            exists = db.query(Ingredient).filter(or_(Ingredient.short==item['short'], Ingredient.name==item['name'])).first()
            if not exists:
                db.add(Ingredient(**item))
                logging.info(f"Initializing default ingredient {item['name']} ({item['short']})")
    
    db.commit()
    db.close()