from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
# importing the router file, tat were seperated to organize the code
from Routers import endpoints
from fastapi.staticfiles import StaticFiles  


app = FastAPI()
# including the router files
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