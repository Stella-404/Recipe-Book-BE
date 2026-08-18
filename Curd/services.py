from datetime import datetime, timedelta

from fastapi import HTTPException, security
from RecipenMealPlanner import Ingredient, Instruction, Recipe, Users
import jwt

security = security.HTTPBearer()
JWT_SECRET = "SECRET_KEY"
JWT_ALGORITHM = "HS256"

def getUserID(credentials):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, JWT_ALGORITHM)
        user_id = payload.get("id")
        if user_id is None:
            raise HTTPException(status_code=403, detail="Invalid token payload")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized. Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def Register(user_data, db):
    existing_user = db.query(Users).filter(Users.email == user_data.email).first()
    if existing_user:
        # giving a BAD REQUEST error code
        raise HTTPException(status_code=400, detail="Email is already registered!")

    new_user = Users(
        username = user_data.username,
        email = user_data.email,
        password = user_data.password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "message": "You have been successfully registered"
    }

def Login(login_data, db):
    user = db.query(Users).filter(Users.email == login_data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Icorrect Email or Password. Try Again")

    if user.password != login_data.password:
        raise HTTPException(status_code=404, detail="Icorrect Email or Password. Try Again")

    token_expiration= datetime.now() + timedelta(hours=1)

    jwt_claims = {
        "username": user.username,
        "id": user.id,
        "exp": token_expiration
    }
    # generating the token
    token = jwt.encode(jwt_claims, JWT_SECRET, JWT_ALGORITHM)

    return {
        "message": "Login Successful",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "name": user.username,
            "id": user.id
        }
    }

def createRecipe(recipe_data, user_id, db):
    # validating the title name
    existing_recipe_title = db.query(Recipe).filter(Recipe.user_id == user_id, Recipe.title == recipe_data.title).first()
    if existing_recipe_title:
            raise HTTPException(status_code=400, detail="This recipe title already exists!")

    # if the title doesn't exist, create the task
    new_recipe = Recipe(
        user_id = user_id,
        title = recipe_data.title,
        description = recipe_data.description,
        cuisine=recipe_data.cuisine,
        category=recipe_data.category,
        prep_time=recipe_data.prep_time,
        cook_time=recipe_data.cook_time,
        servings=recipe_data.servings,
        difficulty=recipe_data.difficulty,
        image_path=recipe_data.image_path
    )

    for ing in recipe_data.ingredients:
        recipe_ingredients = Ingredient(
            name = ing.name,
            quantity = ing.quantity,
            unit= ing.unit
        )
        new_recipe.ingredients.append(recipe_ingredients)

    for inst in recipe_data.instructions:
        recipe_instructions = Instruction(
            stepNumber = inst.stepNumber,
            description = inst.description
        )
        new_recipe.instructions.append(recipe_instructions)

    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)

    return {
        "message": "Recipe created successfully!",
        "recipe_id": new_recipe.id
    }

def getRecipes(user_id, db):
    existing_recipe = db.query(Recipe).filter(Recipe.user_id == user_id).all()

    if not existing_recipe:
        raise HTTPException(status_code=404, detail="No recipes found!")

    return{
        "recipes": existing_recipe,
        "message": "These receipes are found"    
    }

def getRecipeDetails(recipe_id, user_id, db):
    recipe = db.query(Recipe).filter(Recipe.user_id == user_id, Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found!")
    ingredients = recipe.ingredients
    instructions = recipe.instructions
    return{
        "recipe": recipe,
        "ingredients": ingredients,
        "instructions": instructions
    }

def deleteRecipe(recipe_id, user_id, db):
    recipe = db.query(Recipe).filter(Recipe.user_id == user_id, Recipe.id == recipe_id).first()
    if not recipe: 
        raise HTTPException(status_code=404, detail="Recipe not found! probably you deleted it but my application is glitching")

    db.delete(recipe)
    db.commit()
    return{
        "recipe_id": recipe_id,
        "message": "Recipe deleted successfully!"
    }