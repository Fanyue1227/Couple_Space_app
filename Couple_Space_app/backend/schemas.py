from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel

# User Schemas
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    role: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str

# Site Config Schemas
class SiteConfigBase(BaseModel):
    boy_name: str
    girl_name: str
    start_date: datetime
    bg_image: Optional[str] = None
    memory_bg: Optional[str] = None
    album_bg: Optional[str] = None
    lovelist_bg: Optional[str] = None
    boy_avatar: Optional[str] = None
    girl_avatar: Optional[str] = None
    site_title: str

class SiteConfigCreate(SiteConfigBase):
    pass

class SiteConfig(SiteConfigBase):
    id: int
    
    class Config:
        from_attributes = True

# Memory Day Schemas
class MemoryDayPhotoBase(BaseModel):
    url: str

class MemoryDayPhoto(MemoryDayPhotoBase):
    id: int
    memory_day_id: int
    
    class Config:
        from_attributes = True

class MemoryDayBase(BaseModel):
    title: str
    date: date
    description: Optional[str] = None
    icon: Optional[str] = "❤️"

class MemoryDayCreate(MemoryDayBase):
    pass

class MemoryDay(MemoryDayBase):
    id: int
    created_at: datetime
    photos: List[MemoryDayPhoto] = []
    
    class Config:
        from_attributes = True

# Album Schemas
class AlbumPhotoBase(BaseModel):
    url: str

class AlbumPhoto(AlbumPhotoBase):
    id: int
    album_id: int
    
    class Config:
        from_attributes = True

class AlbumBase(BaseModel):
    description: str
    date: date

class AlbumCreate(AlbumBase):
    photos: List[str] = [] # URLs

class AlbumCommentBase(BaseModel):
    content: str
    username: str # Store the name of the commenter directly for simplicity

class AlbumCommentCreate(AlbumCommentBase):
    pass

class AlbumComment(AlbumCommentBase):
    id: int
    album_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class Album(AlbumBase):
    id: int
    created_at: datetime
    photos: List[AlbumPhoto] = []
    comments: List[AlbumComment] = []
    
    class Config:
        from_attributes = True

# Love List Schemas
class LoveListBase(BaseModel):
    title: str
    is_completed: bool = False
    image_url: Optional[str] = None

class LoveListCreate(LoveListBase):
    pass

class LoveList(LoveListBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
