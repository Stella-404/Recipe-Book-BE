from datetime import datetime, timedelta
import json
import os

from fastapi import HTTPException, security
from RecipenMealPlanner import Favorite, Ingredient, Instruction, Recipe, Tag, Users
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



# Directory where images are stored
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def createRecipe(title, description, cuisine, category, prep_time,
    cook_time, servings, difficulty, tags_id, ingredients, instructions, image_path, user_id, db):
    # validating the title name
    existing_recipe_title = db.query(Recipe).filter(Recipe.user_id == user_id, Recipe.title == title).first()
    if existing_recipe_title:
            raise HTTPException(status_code=400, detail="This recipe title already exists!")

    # Paresing the ingredients and instruction fields
    parse_ingredients = json.loads(ingredients)
    parse_instructions = json.loads(instructions)

    # if the title doesn't exist, create the task
    new_recipe = Recipe(
        user_id = user_id,
        title = title,
        description = description,
        cuisine= cuisine,
        category=category,
        prep_time=prep_time,
        cook_time=cook_time,
        servings=servings,
        difficulty=difficulty,
        image_path= None,
    )

    for ing in parse_ingredients:
        recipe_ingredients = Ingredient(
            name = ing.get("name"),
            quantity = ing.get("quantity"),
            unit= ing.get("unit"),
        )
        new_recipe.ingredients.append(recipe_ingredients)

    for inst in parse_instructions:
        recipe_instructions = Instruction(
            stepNumber = inst.get("stepNumber"),
            description = inst.get("description")
        )
        new_recipe.instructions.append(recipe_instructions)

    # === 6. HANDLE TAGS HERE ===
    if tags_id:
        try:
            # Parse the JSON string array (e.g., "[1, 3, 5]") back into a Python list
            parsed_tag_ids = json.loads(tags_id)
            if parsed_tag_ids:
                # Query database for tags whose IDs match the selected list
                existing_tags = db.query(Tag).filter(Tag.id.in_(parsed_tag_ids)).all()
                # Attach them to the recipe's many-to-many relationship
                new_recipe.tags.extend(existing_tags)
        except Exception as e:
            print(f"--- ERROR PARSING TAGS: {str(e)} ---")

    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)

    if image_path and image_path.filename:
        print(f"--- IMAGE RECEIVED: {image_path.filename} ---")
        try: 
            file_name = new_recipe.id
            file_extension = os.path.splitext(image_path.filename)[1]
            new_filename = f"{file_name}{file_extension}"
            file_location = os.path.join(UPLOAD_DIR, new_filename)

            # Save file to disk
            with open(file_location, "wb+") as file_object:
                file_object.write(await image_path.read())

            # Update database record with the final file path/name
            new_recipe.image_path = f"/{UPLOAD_DIR}/{new_filename}"
            db.commit()
            print(f"--- IMAGE SAVED SUCCESSFULLY TO: {file_location} ---")
        except Exception as e:
            print(f"--- ERROR SAVING IMAGE: {str(e)} ---")
    else:
        print("--- NO IMAGE OR EMPTY FILENAME RECEIVED ---")

    return {
        "message": "Recipe created successfully!",
        "recipe_id": new_recipe.id
    }

def getRecipes(user_id, db):
    existing_recipe = db.query(Recipe).filter(Recipe.user_id == user_id).all()

    if not existing_recipe:
        raise HTTPException(status_code=404, detail="No recipes found!")

    fav_recipes = db.query(Favorite).filter(Favorite.user_id == user_id).all()
    fav_ids = {fav.recipe_id for fav in fav_recipes} # Example: {2, 5, 8}

    # Build the response list, tagging each recipe
    # even I don't know what this is x_x
    recipe_list = []
    for recipe in existing_recipe:
        # Extractig tags for EAC Specific recipe
        recipe_tags = [{"id": tag.id, "name": tag.name} for tag in recipe.tags]

        recipe_list.append({
            "id": recipe.id,
            "title": recipe.title,
            "description": recipe.description,
            "cuisine": recipe.cuisine,
            "category": recipe.category,
            "is_favorite": recipe.id in fav_ids,
            "tags": recipe_tags
        })
    
    return{
        "recipes": recipe_list,
        "message": "These receipes are found"    
    }

def getRecipeDetails(recipe_id, user_id, db):
    recipe = db.query(Recipe).filter(Recipe.user_id == user_id, Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found!")
    ingredients = recipe.ingredients
    instructions = recipe.instructions
    tags = recipe.tags
    return{
        "recipe": recipe,
        "ingredients": ingredients,
        "instructions": instructions,
        "tags": tags
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

async def updateRecipe(recipe_id, title, description, cuisine, category, prep_time,
    cook_time, servings, difficulty, ingredients, instructions, image_path, existing_image_path, user_id, db):
    # validating the recipe existence
    existing_recipe = db.query(Recipe).filter(Recipe.user_id == user_id, Recipe.id == recipe_id).first()
    if not existing_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found x_x!")

    # # Paresing the ingredients and instruction fields
    parse_ingredients = json.loads(ingredients)
    parse_instructions = json.loads(instructions)

    # # if the title doesn't exist, create the task
    existing_recipe.user_id = user_id
    existing_recipe.title = title
    existing_recipe.description = description
    existing_recipe.cuisine= cuisine
    existing_recipe.category=category
    existing_recipe.prep_time=prep_time
    existing_recipe.cook_time=cook_time
    existing_recipe.servings=servings
    existing_recipe.difficulty=difficulty

    existing_recipe.ingredients.clear()
    existing_recipe.instructions.clear()

    for ing in parse_ingredients:
        recipe_ingredients = Ingredient(
            name = ing.get("name"),
            quantity = ing.get("quantity"),
            unit= ing.get("unit"),
        )
        existing_recipe.ingredients.append(recipe_ingredients)

    for inst in parse_instructions:
        recipe_instructions = Instruction(
            stepNumber = inst.get("stepNumber"),
            description = inst.get("description")
        )
        existing_recipe.instructions.append(recipe_instructions)

    db.commit()
    db.refresh(existing_recipe)

    if image_path is not None and image_path.filename:
        print(f"--- IMAGE RECEIVED: {image_path.filename} ---")
        try: 
            file_name = existing_recipe.id
            file_extension = os.path.splitext(image_path.filename)[1]
            new_filename = f"{file_name}{file_extension}"
            file_location = os.path.join(UPLOAD_DIR, new_filename)

            # Save file to disk
            with open(file_location, "wb+") as file_object:
                file_object.write(await image_path.read())

            # Update database record with the final file path/name
            existing_recipe.image_path = f"/{UPLOAD_DIR}/{new_filename}"
            db.commit()
            print(f"--- IMAGE SAVED SUCCESSFULLY TO: {file_location} ---")
        except Exception as e:
            print(f"--- ERROR SAVING IMAGE: {str(e)} ---")
    else:
        print("--- NO NEW IMAGE RECEIVED ---")
        existing_recipe.image_path = existing_image_path

    return {
        "message": "Recipe updated successfully!",
        "recipe_id": existing_recipe.id
    }

def favoriteRecipe(r_recipe_id, r_user_id ,db):

# wondering why it is "r_recipe_id" and "r_user_id"? No specific reason, just had to seperate the incoming data 
# from frontend, from the column names....... meh

    # CHECK 1: If the recipe xists
    recipe_exist = db.query(Recipe).filter(Recipe.user_id == r_user_id, Recipe.id == r_recipe_id).first()

    if not recipe_exist:
        raise HTTPException(status_code=404, detail="Recipe not found!")

    # if recipe exists, then check if it is already marked as fav:
    favorite = db.query(Favorite).filter(Favorite.recipe_id == r_recipe_id).first()
    # if already marked as fav
    if favorite:
        # remove from favourites
        db.delete(favorite)
        db.commit()
        return {"is_favorite": False, "message": "Removed from favorites"}
    else:
        # when not already in their favorite list -- Like Us '_'
        new_favorite = Favorite(
            recipe_id = r_recipe_id,
            user_id = r_user_id)
        db.add(new_favorite)
        db.commit()
        return {"is_favorite": True, "message": "Recipe added to favorites"}

def getFavorites(user_id, db):

    fav_recipes = db.query(Favorite).filter(Favorite.user_id == user_id).all()

    if not fav_recipes:
        raise HTTPException(status_code=404, detail="Favorite Recipes not found!")

    # Build the list and explicitly tag each as a favorite
    favorite_recipes = []
    for fav in fav_recipes:
        recipe_data = {
            "id": fav.recipe.id,
            "title": fav.recipe.title,
            "description": fav.recipe.description,
            "category": fav.recipe.category,
            "cuisine": fav.recipe.cuisine,
            "is_favorite": True  # Crucial so the heart shows up red!
        }
        favorite_recipes.append(recipe_data)

    return{
        "recipes": favorite_recipes,
        "message": "Favorite recipes found"
    }

def getTags(db):
    tags = db.query(Tag).all()

    return tags
