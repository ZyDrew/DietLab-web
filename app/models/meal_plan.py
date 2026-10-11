from typing import Optional
from app.database import Base
import datetime
from sqlalchemy import ForeignKey, Date, String, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

class MealPlan(Base):
    __tablename__ = "meal_plan"    

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    start_date: Mapped[datetime.date] = mapped_column(Date)
    name: Mapped[str] = mapped_column(String(100))
    number: Mapped[int] = mapped_column(Integer)
    goal: Mapped[Optional[str]] = mapped_column(Text)

    __table_args__ = (UniqueConstraint("patient_id", "number", name="uc_patient_meal_plan"),)

    def __repr__(self):
        return f"Plan alimentaire(id={self.id}, id_patient={self.patient_id}, date de début={self.start_date}, nom={self.name}, numéro={self.number}, objectif={self.goal})"