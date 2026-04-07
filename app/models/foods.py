from app.database import Base
from sqlalchemy import String, Numeric
from sqlalchemy.orm import Mapped, mapped_column

class Foods(Base):
    __tablename__ = "foods"    

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    calories: Mapped[float] = mapped_column(Numeric(6,2))
    proteins: Mapped[float] = mapped_column(Numeric(6,2))
    fat: Mapped[float] = mapped_column(Numeric(6,2))
    carbs: Mapped[float] = mapped_column(Numeric(6,2))
    calcium: Mapped[float] = mapped_column(Numeric(6,2))
    iron: Mapped[float] = mapped_column(Numeric(6,2))
    vitamin_c: Mapped[float] = mapped_column(Numeric(6,2))

    def __repr__(self):
        return f"Aliment(id={self.id}, nom={self.name}, calories={self.calories}, protéines={self.proteins}, lipides={self.fat}, glucides={self.carbs}, calcium={self.calcium}, fer={self.iron}, vitamine C={self.vitamin_c})"