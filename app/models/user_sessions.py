from app.database import Base
import datetime
from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

class UserSessions(Base):
    __tablename__ = "user_sessions"    

    id: Mapped[int] = mapped_column(primary_key=True)
    token_hash: Mapped[str] = mapped_column(String(64))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), index=True)

    __table_args__ = (UniqueConstraint("token_hash", name="uc_user_session_token"),)

    def __repr__(self):
        return f"Session utilisateur(id={self.id}, id_utilisateur={self.user_id}, cree le={self.created_at}, derniere utilisation={self.last_seen_at}, expire le={self.expires_at})"