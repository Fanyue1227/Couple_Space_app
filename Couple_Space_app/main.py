from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from database import engine, Base
from routers import auth, config, memoryday, lovelist, album

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="情侣小站 API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount legacy img directory for compatibility with old data
# Ensure 'static/img' exists or create it
os.makedirs("static/img", exist_ok=True)
app.mount("/img", StaticFiles(directory="static/img"), name="img")


# Routers
app.include_router(auth.router)
app.include_router(config.router)
app.include_router(memoryday.router)
app.include_router(lovelist.router)
app.include_router(album.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to 情侣小站 API"}
