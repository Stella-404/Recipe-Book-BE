from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import EmailStr
from RecipenMealPlanner import Engine
from sqlalchemy.orm import Session, sessionmaker
from Curd.services import Login, Register, createRecipe, deleteRecipe, getEmail, getRecipeDetails, getRecipes
import jwt
from Routers.pydanticModels import LoginSchema, RecipeCreateSchema, RegistratoinSchema

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

def get_user_email(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    # 
    return getEmail(credentials)


@router.post("/register")
def register(user_data: RegistratoinSchema, db: Session = Depends(get_db) ):
    # 
    return Register(user_data, db)

@router.post("/login")
def login(credentials: LoginSchema, db: Session = Depends(get_db) ):
    # 
    return Login(credentials, db)

@router.post("/recipes")
def create_recipe(recipe_data: RecipeCreateSchema, user_email: EmailStr = Depends(get_user_email), db: Session = Depends(get_db)):
    # 
    return createRecipe(recipe_data, user_email, db)

@router.get("/recipes")
def get_recipes(user_email: str = Depends(get_user_email), db : Session = Depends(get_db)):
    # 
    return getRecipes(user_email, db)

@router.get("/recipes/{recipe_id}")
def get_recipe_details(recipe_id: int, user_email: EmailStr = Depends(get_user_email), db: Session = Depends(get_db)):
    # 
    return getRecipeDetails(recipe_id, user_email ,db)

@router.delete("/recipes/{recipe_id}")
def delete_recipe(recipe_id: int, user_email: EmailStr = Depends(get_user_email), db: Session = Depends(get_db)):
    # 
    return deleteRecipe(recipe_id, user_email, db)