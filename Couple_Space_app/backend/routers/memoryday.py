from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import shutil
import os
import uuid
from database import get_db
from models import MemoryDay, MemoryDayPhoto, User
from schemas import MemoryDay as MemoryDaySchema, MemoryDayCreate
from dependencies import get_current_user
from config import get_settings

settings = get_settings()

router = APIRouter(
    prefix="/api/memoryday",
    tags=["memoryday"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[MemoryDaySchema])
def read_memory_days(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(MemoryDay).order_by(MemoryDay.date.desc()).offset(skip).limit(limit).all()
    return items

@router.post("/", response_model=MemoryDaySchema)
def create_memory_day(
    item: MemoryDayCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = MemoryDay(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/{item_id}", response_model=MemoryDaySchema)
def update_memory_day(
    item_id: int,
    item: MemoryDayCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = db.query(MemoryDay).filter(MemoryDay.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    for key, value in item.model_dump().items():
        setattr(db_item, key, value)
        
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{item_id}")
def delete_memory_day(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = db.query(MemoryDay).filter(MemoryDay.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    db.delete(db_item)
    db.commit()
    return {"ok": True}

@router.post("/{item_id}/photo")
async def upload_memory_day_photo(
    item_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = db.query(MemoryDay).filter(MemoryDay.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Generate unique filename
    extension = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{extension}"
    
    # Create upload dir if not exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Save relative path to DB
    relative_path = f"/static/uploads/{filename}"
    db_photo = MemoryDayPhoto(memory_day_id=item_id, url=relative_path)
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    
    return {"url": relative_path, "id": db_photo.id}

@router.delete("/photo/{photo_id}")
def delete_memory_day_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_photo = db.query(MemoryDayPhoto).filter(MemoryDayPhoto.id == photo_id).first()
    if not db_photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    # Optional: Delete file from disk
    # This requires careful handling (e.g. check if used elsewhere, though here it's 1:1)
    if db_photo.url.startswith("/static/uploads/"):
         # Construct absolute path
         filename = os.path.basename(db_photo.url)
         file_path = os.path.join(settings.UPLOAD_DIR, filename)
         if os.path.exists(file_path):
             try:
                 os.remove(file_path)
             except Exception as e:
                 print(f"Error deleting file: {e}")

    db.delete(db_photo)
    db.commit()
    return {"ok": True}
