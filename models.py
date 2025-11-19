"""Database models and schema definitions."""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Movie:
    id: int
    title: str
    note: Optional[str]
    category_id: int
    user1_rating: Optional[int]
    user2_rating: Optional[int]
    watched: bool
    created_at: datetime

@dataclass
class MovieCategory:
    id: int
    name: str

@dataclass
class Activity:
    id: int
    title: str
    note: Optional[str]
    status: str  # 'planned' or 'done'
    created_at: datetime

@dataclass
class Trip:
    id: int
    title: str
    note: Optional[str]
    category_id: int
    created_at: datetime

@dataclass
class TripCategory:
    id: int
    name: str

@dataclass
class TikTokTrend:
    id: int
    title: str
    video_file_id: Optional[str]
    status: str  # 'todo' or 'done'
    created_at: datetime

@dataclass
class PhotoCategory:
    id: int
    title: str
    link: Optional[str]
    description: Optional[str]

@dataclass
class Game:
    id: int
    title: str
    note: Optional[str]
    genre: Optional[str]
    status: str  # 'pending' or 'done'
    user1_rating: Optional[int]
    user2_rating: Optional[int]
    created_at: datetime

@dataclass
class Sexual:
    id: int
    title: str
    link: Optional[str]
    description: Optional[str]
    category_id: int

@dataclass
class SexualCategory:
    id: int
    name: str

