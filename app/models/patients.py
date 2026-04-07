from app.database import Base
import datetime
from typing import Optional
from sqlalchemy import String, Date, Text
from sqlalchemy.orm import Mapped, mapped_column

class Patients(Base):
    __tablename__ = "patients"    

    id: Mapped[int] = mapped_column(primary_key=True)
    lastname: Mapped[str] = mapped_column(String(100))
    firstname: Mapped[str] = mapped_column(String(100))
    birthdate: Mapped[datetime.date] = mapped_column(Date)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    def __repr__(self):
        return f"Patient(id={self.id}, nom={self.lastname}, prénom={self.firstname}, date de naissance={self.birthdate}, notes={self.notes})"