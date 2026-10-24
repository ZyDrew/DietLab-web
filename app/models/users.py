from app.database import Base
import datetime
from sqlalchemy import CheckConstraint, DateTime, String, Text, Boolean, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

class Users(Base):
    __tablename__ = "users"    

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("email", name="uc_user_email"),CheckConstraint("email = lower(email)", name="ck_user_email_lowercase"),)

    def __repr__(self):
        return f"Utilisateur(id={self.id}, email={self.email}, actif={self.is_active}, cree le={self.created_at})"