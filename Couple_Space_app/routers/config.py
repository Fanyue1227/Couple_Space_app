from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import shutil
import os
import uuid
from database import get_db
from models import SiteConfig, User
from schemas import SiteConfigCreate, SiteConfig as SiteConfigSchema
from dependencies import get_current_user
from config import get_settings

settings = get_settings()

router = APIRouter(
    prefix="/api/config",
    tags=["config"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=SiteConfigSchema)
def get_site_config(db: Session = Depends(get_db)):
    config = db.query(SiteConfig).first()
    if not config:
        # Return default if not exists
        return {
            "id": 0,
            "boy_name": "Boy",
            "girl_name": "Girl",
            "start_date": "2025-01-01T00:00:00",
            "site_title": "Our Love Story"
        }
    return config

@router.put("/", response_model=SiteConfigSchema)
def update_site_config(
    config: SiteConfigCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_config = db.query(SiteConfig).first()
    if not db_config:
        db_config = SiteConfig(**config.model_dump())
        db.add(db_config)
    else:
        for key, value in config.model_dump().items():
            setattr(db_config, key, value)
    
    db.commit()
    db.refresh(db_config)
    return db_config

@router.post("/upload-avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    # Generate unique filename
    extension = os.path.splitext(file.filename)[1]
    filename = f"avatar_{uuid.uuid4()}{extension}"
    
    # Create upload dir
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    relative_path = f"/static/uploads/{filename}"
    return {"url": relative_path}
