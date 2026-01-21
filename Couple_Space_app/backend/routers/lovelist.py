from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import LoveList, User
from schemas import LoveList as LoveListSchema, LoveListCreate
from dependencies import get_current_user

router = APIRouter(
    prefix="/api/lovelist",
    tags=["lovelist"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[LoveListSchema])
def read_lovelist(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(LoveList).order_by(LoveList.created_at.desc()).offset(skip).limit(limit).all()
    return items

@router.post("/", response_model=LoveListSchema)
def create_lovelist_item(
    item: LoveListCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = LoveList(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/{item_id}", response_model=LoveListSchema)
def update_lovelist_item(
    item_id: int,
    item: LoveListCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = db.query(LoveList).filter(LoveList.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    for key, value in item.model_dump().items():
        setattr(db_item, key, value)
        
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{item_id}")
def delete_lovelist_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = db.query(LoveList).filter(LoveList.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    db.delete(db_item)
    db.commit()
    return {"ok": True}

@router.post("/{item_id}/photo")
async def upload_lovelist_photo(
    item_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    import os
    import shutil
    import uuid
    from models import LoveList
    from config import get_settings
    
    settings = get_settings()
    
    db_item = db.query(LoveList).filter(LoveList.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Generate unique filename
    extension = os.path.splitext(file.filename)[1]
    filename = f"lovelist_{uuid.uuid4()}{extension}"
    
    # Create upload dir if not exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Save relative path to DB
    relative_path = f"/static/uploads/{filename}"
    db_item.image_url = relative_path
    db.commit()
    db.refresh(db_item)
    
    return {"url": relative_path}
