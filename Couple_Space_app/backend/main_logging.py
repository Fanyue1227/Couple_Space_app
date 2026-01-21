from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse
import os
from database import engine, Base
from routers import auth, config, memoryday, lovelist, album
import logging

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="情侣小站 API")

# Logging Exception Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_details = exc.errors()
    print(f"❌ Validation Error for {request.method} {request.url}")
    print(f"Error Details: {error_details}")
    try:
        body = await request.json()
        print(f"Request Body: {body}")
    except:
        print("Could not parse body")
        
    return JSONResponse(
        status_code=422,
        content={"detail": error_details},
    )

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
