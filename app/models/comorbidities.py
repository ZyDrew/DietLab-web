from app.database import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

class Comorbidities(Base):
    __tablename__ = "comorbidities"    

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    def __repr__(self):
        return f"Comorbidité(id={self.id}, nom={self.name})"