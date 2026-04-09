from app.database import Base
from app.models.enums import MealPlanEnum
from sqlalchemy import ForeignKey, Integer, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

class MealPlanFood(Base):
    __tablename__ = "meal_plan_food"    

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("meal_plan.id"))
    food_id: Mapped[int] = mapped_column(ForeignKey("foods.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    period: Mapped[MealPlanEnum] = mapped_column(Enum(MealPlanEnum))
    frequency: Mapped[int] = mapped_column(Integer)

    __table_args__ = (UniqueConstraint("plan_id", "food_id", "period", name="uc_meal_plan_food"),)

    def __repr__(self):
        return f"Plan alimentaire - aliments(id={self.id}, id_plan={self.plan_id}, id_aliment={self.food_id}, quantité={self.quantity}, période={self.period}, fréquence={self.frequency})"