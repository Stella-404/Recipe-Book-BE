from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
# importing the router file, tat were seperated to organize the code
from RecipenMealPlanner import Base, Engine, Tag
from Routers import endpoints
from fastapi.staticfiles import StaticFiles  

# Base.metadata.create_all(bind = Engine)
app = FastAPI()
# including the router files
DEFAULT_TAGS = ["Vegan", "Vegetarian", "Gluten-free", "Low-carb", "Dairy-free", "Spicy", "Slow cooked", "Quick meal", "One-pot",
                "Oven-Baked", "Air-fryed", "Grill", "Appetizer", "Nut-free", "Under 30 min", "Meal Prep", "No-Cook", "No-Oven"]

try:
    print("Attempting to create database tables...")
    Base.metadata.create_all(bind=Engine)
    print("Tables created successfully.")

    print("Attempting to seed tags...")
    db = endpoints.SessionLocal()
    try:
        if db.query(Tag).count() == 0:
            for name in DEFAULT_TAGS:
                db.add(Tag(name=name))
            db.commit()
            print(">>> DEFAULT TAGS SEEDED SUCCESSFULLY! <<<")
        else:
            print(">>> Tags already exist in database. <<<")
    finally:
        db.close()
except Exception as e:
    print(f"\n❌ STARTUP FAILED WITH ERROR: {e}\n")
    raise e

app.include_router(endpoints.router)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

#  Enable CORS so REACT can communicate with FASTAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)