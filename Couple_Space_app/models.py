from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(100))
    is_active = Column(Boolean, default=True)
    role = Column(String(20), default="admin") # boy, girl, admin

class SiteConfig(Base):
    __tablename__ = "site_config"
    __table_args__ = {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
    
    id = Column(Integer, primary_key=True)
    boy_name = Column(String(50))
    girl_name = Column(String(50))
    start_date = Column(DateTime)
    bg_image = Column(String(255)) # Default/Home
    memory_bg = Column(String(255), nullable=True)
    album_bg = Column(String(255), nullable=True)
    lovelist_bg = Column(String(255), nullable=True)
    boy_avatar = Column(String(255), nullable=True)
    girl_avatar = Column(String(255), nullable=True)
    site_title = Column(String(100))

class MemoryDay(Base):
    __tablename__ = "memory_days"
    __table_args__ = {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True)
    date = Column(Date)
    description = Column(Text, nullable=True)
    icon = Column(String(50), default="❤️")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    photos = relationship("MemoryDayPhoto", back_populates="memory_day", cascade="all, delete-orphan")

class MemoryDayPhoto(Base):
    __tablename__ = "memory_day_photos"
    __table_args__ = {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
    
    id = Column(Integer, primary_key=True, index=True)
    memory_day_id = Column(Integer, ForeignKey("memory_days.id"))
    url = Column(String(255))
    
    memory_day = relationship("MemoryDay", back_populates="photos")

class Album(Base):
    __tablename__ = "albums"
    __table_args__ = {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
    
    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text) # from imgText
    date = Column(Date) # from imgDatd
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    photos = relationship("AlbumPhoto", back_populates="album", cascade="all, delete-orphan")
    comments = relationship("AlbumComment", back_populates="album", cascade="all, delete-orphan")

class AlbumPhoto(Base):
    __tablename__ = "album_photos"
    __table_args__ = {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
    
    id = Column(Integer, primary_key=True, index=True)
    album_id = Column(Integer, ForeignKey("albums.id"))
    url = Column(String(255))
    
    album = relationship("Album", back_populates="photos")
    
class AlbumComment(Base):
    __tablename__ = "album_comments"
    __table_args__ = {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
    
    id = Column(Integer, primary_key=True, index=True)
    album_id = Column(Integer, ForeignKey("albums.id"))
    username = Column(String(50))
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    album = relationship("Album", back_populates="comments")

class LoveList(Base):
    __tablename__ = "love_list"
    __table_args__ = {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    is_completed = Column(Boolean, default=False)
    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
