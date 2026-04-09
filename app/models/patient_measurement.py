from app.database import Base
import datetime
from sqlalchemy import Numeric, Date, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

class PatientMeasurement(Base):
    __tablename__ = "patient_measurement"    

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    height: Mapped[float] = mapped_column(Numeric(6,2))
    weight: Mapped[float] = mapped_column(Numeric(6,2))
    record_date: Mapped[datetime.date] = mapped_column(Date, server_default=func.current_date()) 

    def __repr__(self):
        return f"Mesure patient(id={self.id}, id_patient={self.patient_id}, taille={self.height}, poids={self.weight}, date de prise={self.record_date})"