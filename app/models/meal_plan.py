from app.database import Base
import datetime
from sqlalchemy import ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column

class MealPlan(Base):
    __tablename__ = "meal_plan"    

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    start_date: Mapped[datetime.date] = mapped_column(Date)

    def __repr__(self):
        return f"Plan alimentaire(id={self.id}, id_patient={self.patient_id}, date de début={self.start_date})"