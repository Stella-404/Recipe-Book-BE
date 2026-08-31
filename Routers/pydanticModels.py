from datetime import date
from typing import List, Optional
from pydantic import BaseModel, EmailStr

# Pydantic Models
class RegistratoinSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

# ---------- RELATIONAL / NESTED TABLE
# a table is termed as nested if it has multiple tables linked with it
# the table contins list of ingredients (a separate table)
# it contains a list of instructions ( which is also a while separeate table linked with it)

class IngredientSchema(BaseModel):
    name: str
    quantity: float
    unit: str

class InstructionSchema(BaseModel):
    stepNumber: int
    description: str

class RecipeBaseSchema(BaseModel):
    # user_email: EmailStr
    title: str
    description: Optional[str]
    cuisine: str
    category: str
    prep_time: str
    cook_time: str
    servings: int
    difficulty: str
    image_path: Optional[str]
    tags_id: Optional[List[int]]

class RecipeCreateSchema(RecipeBaseSchema):
    ingredients: List[IngredientSchema]
    instructions: List[InstructionSchema]

class MealPlannerSchema(BaseModel):
    week_start_date: date
    day_of_week: int
    meal_slot: str
    recipe_name: str

class ShoppingList(BaseModel):
    id: int
    ing_name: str
    total_quantity: float
    unit: int
    is_purchased: bool