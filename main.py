from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from database import engine
from routers import auth_routes, conversation_routes

app = FastAPI(title="AuchenCore AI")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change later to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create DB tables
SQLModel.metadata.create_all(engine)

# Include routers
app.include_router(auth_routes.router)
app.include_router(conversation_routes.router)
