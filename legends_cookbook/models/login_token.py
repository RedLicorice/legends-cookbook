from sqlalchemy.orm import  Mapped, relationship, mapped_column
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, DateTime, ForeignKey, Boolean
from typing import Optional, List, TYPE_CHECKING
from .base import Base
from datetime import datetime, timedelta, UTC as UTC_TZ
if TYPE_CHECKING:
    from .user import User

class LoginToken(Base):
    __tablename__ = 'login_tokens'
    id = mapped_column(Integer, primary_key=True, index=True)

    # Token Owner
    telegram_user_id: Mapped[str] = mapped_column(ForeignKey("users.telegram_user_id"))
    user: Mapped["User"] = relationship(back_populates="login_tokens")
    
    # Authentication Token information
    token = mapped_column(String, unique=True)
    expires = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC_TZ) + timedelta(minutes=3))

    used = mapped_column(Boolean, default=False)
    active = mapped_column(Boolean, default=True)

    # Common
    created = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_updated = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())