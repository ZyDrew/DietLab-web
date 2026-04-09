from app.database import Base
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

class PatientComorbidity(Base):
    __tablename__ = "patient_comorbidity"    

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    comorbidity_id: Mapped[int] = mapped_column(ForeignKey("comorbidities.id"))

    __table_args__ = (UniqueConstraint("patient_id", "comorbidity_id", name="uc_patient_comorbidity"),)
    
    def __repr__(self):
        return f"Comorbidité du patient(id={self.id}, id_patient={self.patient_id}, id_comorbidité={self.comorbidty_id})"