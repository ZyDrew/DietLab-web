from app.database import Base
from app.models.enums import AppointmentEnum
import datetime
from typing import Optional
from sqlalchemy import DateTime, Text, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

class Appointments(Base):
    __tablename__ = "appointments"    

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    date_time: Mapped[datetime.datetime] = mapped_column(DateTime)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    type: Mapped[AppointmentEnum] = mapped_column(Enum(AppointmentEnum))

    def __repr__(self):
        return f"Rendez-vous(id={self.id}, id_patient={self.patient_id}, date et heure={self.date_time}, notes={self.notes}, type de rdv={self.type})"