from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import EmailStr
from RecipenMealPlanner import Engine
from sqlalchemy.orm import Session, sessionmaker
from Curd.services import Login, Register, createRecipe, deleteRecipe, favoriteRecipe, getFavorites, getRecipeDetails, getRecipes, getUserID, updateRecipe
import jwt
from Routers.pydanticModels import LoginSchema, RecipeCreateSchema, RegistratoinSchema
import os

# creating the router instance
router = APIRouter(
    prefix = "/api",
    tags = ["user"]
)

SessionLocal = sessionmaker(bind=Engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

security = HTTPBearer()

def get_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    # 
    return getUserID(credentials)


@router.post("/register")
def register(user_data: RegistratoinSchema, db: Session = Depends(get_db) ):
    # 
    return Register(user_data, db)

@router.post("/login")
def login(credentials: LoginSchema, db: Session = Depends(get_db) ):
    # 
    return Login(credentials, db)

@router.post("/recipes")
async def create_recipe(title: str = Form(...),
    description: str = Form(None),  # Optional field
    cuisine: str = Form(...),
    category: str = Form(...),
    prep_time: int = Form(...),
    cook_time: int = Form(...),
    servings: int = Form(...),
    difficulty: str = Form(...),
    ingredients: str = Form(...),  # Received as a JSON string from frontend
    instructions: str = Form(...),  # Received as a JSON string from frontend
    image_path: UploadFile = File(None), 
    user_id: int = Depends(get_user_id), db: Session = Depends(get_db)):
    # 
    return await createRecipe(title, description, cuisine, category, prep_time,
    cook_time, servings, difficulty, ingredients, instructions, image_path, user_id, db)

@router.get("/recipes")
def get_recipes(user_id: int = Depends(get_user_id), db : Session = Depends(get_db)):
    # 
    return getRecipes(user_id, db)

@router.get("/recipes/{recipe_id}")
def get_recipe_details(recipe_id: int, user_id: int = Depends(get_user_id), db: Session = Depends(get_db)):
    # 
    return getRecipeDetails(recipe_id, user_id ,db)

@router.delete("/recipes/{recipe_id}")
def delete_recipe(recipe_id: int, user_id: int = Depends(get_user_id), db: Session = Depends(get_db)):
    # 
    return deleteRecipe(recipe_id, user_id, db)

@router.put("/recipes/{recipe_id}/edit")
async def update_recipe( recipe_id: int,
    title: str = Form(...),
    description: str = Form(None),  # Optional field
    cuisine: str = Form(...),
    category: str = Form(...),
    prep_time: int = Form(...),
    cook_time: int = Form(...),
    servings: int = Form(...),
    difficulty: str = Form(...),
    ingredients: str = Form(...),
    instructions: str = Form(...),
    image_path: UploadFile = File(None), 
    existing_image_path: str = Form(None),
    user_id: int = Depends(get_user_id), db: Session = Depends(get_db)):
    # 
    return await updateRecipe(recipe_id, title, description, cuisine, category, prep_time,
    cook_time, servings, difficulty, ingredients, instructions, image_path, existing_image_path, user_id, db)

@router.post("/recipes/{recipe_id}/favorites")
def favorite_recipe(recipe_id: int, user_id: int = Depends(get_user_id), db: Session = Depends(get_db)):
    # 
    return favoriteRecipe(recipe_id, user_id ,db)

@router.get("/favorites")
def get_favorite_recipes(user_id: int = Depends(get_user_id), db : Session = Depends(get_db)):
    # 
    return getFavorites(user_id, db)
