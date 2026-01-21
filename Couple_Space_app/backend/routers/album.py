from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import shutil
import os
import uuid
from database import get_db
from models import Album, AlbumPhoto, AlbumComment, User
from schemas import Album as AlbumSchema, AlbumCreate, AlbumCommentCreate
from dependencies import get_current_user
from config import get_settings

settings = get_settings()

router = APIRouter(
    prefix="/api/album",
    tags=["album"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[AlbumSchema])
def read_albums(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(Album).order_by(Album.date.desc()).offset(skip).limit(limit).all()
    return items

@router.post("/", response_model=AlbumSchema)
def create_album(
    item: AlbumCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = Album(description=item.description, date=item.date)
    db.add(db_item)
    db.flush() # Get ID
    
    # Add photos if URLs provided
    for photo_url in item.photos:
        db_photo = AlbumPhoto(album_id=db_item.id, url=photo_url)
        db.add(db_photo)
    
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/{item_id}", response_model=AlbumSchema)
def update_album(
    item_id: int,
    item: AlbumCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = db.query(Album).filter(Album.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db_item.description = item.description
    db_item.date = item.date
    
    # Handle photos update? 
    # For now, let's keep it simple: update metadata only. 
    # Photos are managed by create/delete/upload separately or we can overwrite if needed.
    # The current AlbumCreate schema has 'photos' list. 
    # If we want to support sync photos list, we need more logic (delete removed, add new).
    # Given the UI usually just adds photos, let's focus on Description/Date first which are missing.
    
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{item_id}")
def delete_album(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = db.query(Album).filter(Album.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    db.delete(db_item)
    db.commit()
    return {"ok": True}

@router.post("/upload")
async def upload_album_photo(
    file: UploadFile = File(...),
    album_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate album exists
    db_album = db.query(Album).filter(Album.id == album_id).first()
    if not db_album:
        raise HTTPException(status_code=404, detail="Album not found")
    
    # Generate unique filename
    extension = os.path.splitext(file.filename)[1]
    filename = f"album_{uuid.uuid4()}{extension}"
    
    # Create upload dir
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Save photo to database
    relative_path = f"/static/uploads/{filename}"
    db_photo = AlbumPhoto(album_id=album_id, url=relative_path)
    db.add(db_photo)
    db.commit()
    
    return {"url": relative_path}

@router.delete("/photo/{photo_id}")
def delete_album_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_photo = db.query(AlbumPhoto).filter(AlbumPhoto.id == photo_id).first()
    if not db_photo:
        raise HTTPException(status_code=404, detail="Photo not found")
        
    # Delete file from disk
    if db_photo.url.startswith("/static/uploads/"):
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

@router.post("/{item_id}/comments", response_model=AlbumSchema)
def create_comment(
    item_id: int,
    comment: AlbumCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify album exists
    db_album = db.query(Album).filter(Album.id == item_id).first()
    if not db_album:
        raise HTTPException(status_code=404, detail="Album not found")
        
    # Create comment
    # Use the username from the request body as per schema design (simplicity)
    # Or override with current_user.username if we prefer strict auth
    # Let's use current_user.username for consistency if the frontend sends it or not
    # Actually, schema has username. Let's trust frontend or use current_user?
    # Let's stick to Schema for now but default to current_user if empty? 
    # For now, let's just use the schema provided username, assuming frontend handles it.
    
    db_comment = AlbumComment(
        album_id=item_id,
        username=comment.username,
        content=comment.content
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_album) # Refresh album to include new comment
    return db_album
