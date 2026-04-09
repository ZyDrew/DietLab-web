from app.database import Base
from app.models.enums import UnitEnum
from sqlalchemy import ForeignKey, UniqueConstraint, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column

class RecipeFood(Base):
    __tablename__ = "recipe_food"    

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"))
    food_id: Mapped[int] = mapped_column(ForeignKey("foods.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    unit: Mapped[UnitEnum] = mapped_column(Enum(UnitEnum))

    __table_args__ = (UniqueConstraint("recipe_id", "food_id", name="uc_recipe_food"),)
    
    def __repr__(self):
        return f"Aliments d'une recette(id={self.id}, id_recette={self.recipe_id}, id_aliment={self.food_id}, quantité={self.quantity}, pièce={self.unit})"