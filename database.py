"""Database operations and initialization."""
import sqlite3
import logging
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime
from config import DATA_DIR

logger = logging.getLogger(__name__)

DB_PATH = DATA_DIR / "multilists.db"

def get_connection():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database with all required tables."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Movies
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movie_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            note TEXT,
            category_id INTEGER NOT NULL,
            user1_rating INTEGER,
            user2_rating INTEGER,
            watched INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES movie_categories(id)
        )
    """)
    
    # Insert default movie categories
    default_movie_categories = ['Фильм', 'Сериал', 'Мультик']
    for cat in default_movie_categories:
        cursor.execute("INSERT OR IGNORE INTO movie_categories (name) VALUES (?)", (cat,))
    
    # Activities
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            note TEXT,
            status TEXT DEFAULT 'planned',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Trips
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trip_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            note TEXT,
            category_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES trip_categories(id)
        )
    """)
    
    # Insert default trip categories
    default_trip_categories = ['Пешком', 'Поездки', 'Места в Херцег-Нови']
    for cat in default_trip_categories:
        cursor.execute("INSERT OR IGNORE INTO trip_categories (name) VALUES (?)", (cat,))
    
    # TikTok Trends
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tiktok_trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            video_file_id TEXT,
            status TEXT DEFAULT 'todo',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Photo Categories
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS photo_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            link TEXT,
            description TEXT
        )
    """)
    
    # Insert default photo categories
    cursor.execute("INSERT OR IGNORE INTO photo_categories (title) VALUES (?)", ('Категория 1',))
    cursor.execute("INSERT OR IGNORE INTO photo_categories (title) VALUES (?)", ('Категория 2',))
    
    # Games
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            note TEXT,
            genre TEXT,
            status TEXT DEFAULT 'pending',
            user1_rating INTEGER,
            user2_rating INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Sexual
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sexual_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sexual (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            link TEXT,
            description TEXT,
            category_id INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES sexual_categories(id)
        )
    """)
    
    # Insert default sexual category
    cursor.execute("INSERT OR IGNORE INTO sexual_categories (name) VALUES (?)", ('Магазины',))
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

# Movie operations
def add_movie(title: str, note: Optional[str], category_id: int) -> int:
    """Add a new movie."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO movies (title, note, category_id) VALUES (?, ?, ?)",
        (title, note, category_id)
    )
    movie_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return movie_id

def get_movies(watched: bool = False, category_id: Optional[int] = None) -> List[sqlite3.Row]:
    """Get movies list."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if category_id:
        cursor.execute(
            "SELECT * FROM movies WHERE watched = ? AND category_id = ? ORDER BY created_at DESC",
            (1 if watched else 0, category_id)
        )
    else:
        cursor.execute(
            "SELECT * FROM movies WHERE watched = ? ORDER BY created_at DESC",
            (1 if watched else 0,)
        )
    
    results = cursor.fetchall()
    conn.close()
    return results

def get_movie(movie_id: int) -> Optional[sqlite3.Row]:
    """Get a single movie."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def update_movie(movie_id: int, title: Optional[str] = None, note: Optional[str] = None):
    """Update movie."""
    conn = get_connection()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if note is not None:
        updates.append("note = ?")
        params.append(note)
    
    if updates:
        params.append(movie_id)
        cursor.execute(f"UPDATE movies SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
    
    conn.close()

def mark_movie_watched(movie_id: int, user1_rating: Optional[int], user2_rating: Optional[int]):
    """Mark movie as watched with ratings."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE movies SET watched = 1, user1_rating = ?, user2_rating = ? WHERE id = ?",
        (user1_rating, user2_rating, movie_id)
    )
    conn.commit()
    conn.close()

def delete_movie(movie_id: int):
    """Delete a movie."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
    conn.commit()
    conn.close()

def get_random_movie(exclude_series: bool = True) -> Optional[sqlite3.Row]:
    """Get a random unwatched movie, optionally excluding series."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if exclude_series:
        # Get category_id for 'Сериал'
        cursor.execute("SELECT id FROM movie_categories WHERE name = ?", ('Сериал',))
        series_cat = cursor.fetchone()
        if series_cat:
            cursor.execute(
                """SELECT * FROM movies WHERE watched = 0 AND category_id != ? 
                   ORDER BY RANDOM() LIMIT 1""",
                (series_cat['id'],)
            )
        else:
            cursor.execute("SELECT * FROM movies WHERE watched = 0 ORDER BY RANDOM() LIMIT 1")
    else:
        cursor.execute("SELECT * FROM movies WHERE watched = 0 ORDER BY RANDOM() LIMIT 1")
    
    result = cursor.fetchone()
    conn.close()
    return result

def get_movie_top10(user_num: Optional[int] = None) -> List[sqlite3.Row]:
    """Get top 10 movies by rating."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if user_num == 1:
        cursor.execute(
            """SELECT * FROM movies WHERE watched = 1 AND user1_rating IS NOT NULL 
               ORDER BY user1_rating DESC LIMIT 10"""
        )
    elif user_num == 2:
        cursor.execute(
            """SELECT * FROM movies WHERE watched = 1 AND user2_rating IS NOT NULL 
               ORDER BY user2_rating DESC LIMIT 10"""
        )
    else:
        cursor.execute(
            """SELECT *, (COALESCE(user1_rating, 0) + COALESCE(user2_rating, 0)) / 2.0 as avg_rating
               FROM movies WHERE watched = 1 
               AND (user1_rating IS NOT NULL OR user2_rating IS NOT NULL)
               ORDER BY avg_rating DESC LIMIT 10"""
        )
    
    results = cursor.fetchall()
    conn.close()
    return results

def get_movie_categories() -> List[sqlite3.Row]:
    """Get all movie categories."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movie_categories ORDER BY name")
    results = cursor.fetchall()
    conn.close()
    return results

def add_movie_category(name: str) -> int:
    """Add a new movie category."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO movie_categories (name) VALUES (?)", (name,))
    cat_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return cat_id

# Activity operations
def add_activity(title: str, note: Optional[str]) -> int:
    """Add a new activity."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO activities (title, note) VALUES (?, ?)",
        (title, note)
    )
    activity_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return activity_id

def get_activities(status: str = 'planned') -> List[sqlite3.Row]:
    """Get activities by status."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM activities WHERE status = ? ORDER BY created_at DESC",
        (status,)
    )
    results = cursor.fetchall()
    conn.close()
    return results

def get_activity(activity_id: int) -> Optional[sqlite3.Row]:
    """Get a single activity."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM activities WHERE id = ?", (activity_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def update_activity(activity_id: int, title: Optional[str] = None, note: Optional[str] = None):
    """Update activity."""
    conn = get_connection()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if note is not None:
        updates.append("note = ?")
        params.append(note)
    
    if updates:
        params.append(activity_id)
        cursor.execute(f"UPDATE activities SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
    
    conn.close()

def mark_activity_done(activity_id: int):
    """Mark activity as done."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE activities SET status = 'done' WHERE id = ?", (activity_id,))
    conn.commit()
    conn.close()

def delete_activity(activity_id: int):
    """Delete an activity."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM activities WHERE id = ?", (activity_id,))
    conn.commit()
    conn.close()

# Trip operations
def add_trip(title: str, note: Optional[str], category_id: int) -> int:
    """Add a new trip."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO trips (title, note, category_id) VALUES (?, ?, ?)",
        (title, note, category_id)
    )
    trip_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return trip_id

def get_trips(category_id: Optional[int] = None) -> List[sqlite3.Row]:
    """Get trips."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if category_id:
        cursor.execute(
            "SELECT * FROM trips WHERE category_id = ? ORDER BY created_at DESC",
            (category_id,)
        )
    else:
        cursor.execute("SELECT * FROM trips ORDER BY created_at DESC")
    
    results = cursor.fetchall()
    conn.close()
    return results

def get_trip(trip_id: int) -> Optional[sqlite3.Row]:
    """Get a single trip."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trips WHERE id = ?", (trip_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def update_trip(trip_id: int, title: Optional[str] = None, note: Optional[str] = None):
    """Update trip."""
    conn = get_connection()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if note is not None:
        updates.append("note = ?")
        params.append(note)
    
    if updates:
        params.append(trip_id)
        cursor.execute(f"UPDATE trips SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
    
    conn.close()

def delete_trip(trip_id: int):
    """Delete a trip."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM trips WHERE id = ?", (trip_id,))
    conn.commit()
    conn.close()

def get_trip_categories() -> List[sqlite3.Row]:
    """Get all trip categories."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trip_categories ORDER BY name")
    results = cursor.fetchall()
    conn.close()
    return results

def add_trip_category(name: str) -> int:
    """Add a new trip category."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO trip_categories (name) VALUES (?)", (name,))
    cat_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return cat_id

# TikTok operations
def add_tiktok_trend(title: str, video_file_id: Optional[str]) -> int:
    """Add a new TikTok trend."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tiktok_trends (title, video_file_id) VALUES (?, ?)",
        (title, video_file_id)
    )
    trend_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return trend_id

def get_tiktok_trends(status: str = 'todo') -> List[sqlite3.Row]:
    """Get TikTok trends by status."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM tiktok_trends WHERE status = ? ORDER BY created_at DESC",
        (status,)
    )
    results = cursor.fetchall()
    conn.close()
    return results

def get_tiktok_trend(trend_id: int) -> Optional[sqlite3.Row]:
    """Get a single TikTok trend."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tiktok_trends WHERE id = ?", (trend_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def mark_tiktok_trend_done(trend_id: int):
    """Mark TikTok trend as done."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tiktok_trends SET status = 'done' WHERE id = ?", (trend_id,))
    conn.commit()
    conn.close()

def delete_tiktok_trend(trend_id: int):
    """Delete a TikTok trend."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tiktok_trends WHERE id = ?", (trend_id,))
    conn.commit()
    conn.close()

# Photo category operations
def get_photo_categories() -> List[sqlite3.Row]:
    """Get all photo categories."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM photo_categories ORDER BY id")
    results = cursor.fetchall()
    conn.close()
    return results

def get_photo_category(category_id: int) -> Optional[sqlite3.Row]:
    """Get a single photo category."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM photo_categories WHERE id = ?", (category_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def add_photo_category(title: str, link: Optional[str], description: Optional[str]) -> int:
    """Add a new photo category."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO photo_categories (title, link, description) VALUES (?, ?, ?)",
        (title, link, description)
    )
    cat_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return cat_id

def update_photo_category(category_id: int, title: Optional[str] = None, 
                         link: Optional[str] = None, description: Optional[str] = None):
    """Update photo category."""
    conn = get_connection()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if link is not None:
        updates.append("link = ?")
        params.append(link)
    if description is not None:
        updates.append("description = ?")
        params.append(description)
    
    if updates:
        params.append(category_id)
        cursor.execute(f"UPDATE photo_categories SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
    
    conn.close()

# Game operations
def add_game(title: str, note: Optional[str], genre: Optional[str]) -> int:
    """Add a new game."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO games (title, note, genre) VALUES (?, ?, ?)",
        (title, note, genre)
    )
    game_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return game_id

def get_games(status: str = 'pending') -> List[sqlite3.Row]:
    """Get games by status."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM games WHERE status = ? ORDER BY created_at DESC",
        (status,)
    )
    results = cursor.fetchall()
    conn.close()
    return results

def get_game(game_id: int) -> Optional[sqlite3.Row]:
    """Get a single game."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM games WHERE id = ?", (game_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def update_game(game_id: int, title: Optional[str] = None, 
               note: Optional[str] = None, genre: Optional[str] = None):
    """Update game."""
    conn = get_connection()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if note is not None:
        updates.append("note = ?")
        params.append(note)
    if genre is not None:
        updates.append("genre = ?")
        params.append(genre)
    
    if updates:
        params.append(game_id)
        cursor.execute(f"UPDATE games SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
    
    conn.close()

def mark_game_done(game_id: int, user1_rating: Optional[int], user2_rating: Optional[int]):
    """Mark game as done with ratings."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE games SET status = 'done', user1_rating = ?, user2_rating = ? WHERE id = ?",
        (user1_rating, user2_rating, game_id)
    )
    conn.commit()
    conn.close()

def delete_game(game_id: int):
    """Delete a game."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM games WHERE id = ?", (game_id,))
    conn.commit()
    conn.close()

def get_random_game() -> Optional[sqlite3.Row]:
    """Get a random pending game."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM games WHERE status = 'pending' ORDER BY RANDOM() LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result

def get_game_top10(user_num: Optional[int] = None) -> List[sqlite3.Row]:
    """Get top 10 games by rating."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if user_num == 1:
        cursor.execute(
            """SELECT * FROM games WHERE status = 'done' AND user1_rating IS NOT NULL 
               ORDER BY user1_rating DESC LIMIT 10"""
        )
    elif user_num == 2:
        cursor.execute(
            """SELECT * FROM games WHERE status = 'done' AND user2_rating IS NOT NULL 
               ORDER BY user2_rating DESC LIMIT 10"""
        )
    else:
        cursor.execute(
            """SELECT *, (COALESCE(user1_rating, 0) + COALESCE(user2_rating, 0)) / 2.0 as avg_rating
               FROM games WHERE status = 'done' 
               AND (user1_rating IS NOT NULL OR user2_rating IS NOT NULL)
               ORDER BY avg_rating DESC LIMIT 10"""
        )
    
    results = cursor.fetchall()
    conn.close()
    return results

# Sexual operations
def add_sexual(title: str, link: Optional[str], description: Optional[str], category_id: int) -> int:
    """Add a new sexual entry."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sexual (title, link, description, category_id) VALUES (?, ?, ?, ?)",
        (title, link, description, category_id)
    )
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return entry_id

def get_sexual_by_category(category_id: Optional[int] = None) -> List[sqlite3.Row]:
    """Get sexual entries by category."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if category_id:
        cursor.execute(
            "SELECT * FROM sexual WHERE category_id = ? ORDER BY id DESC",
            (category_id,)
        )
    else:
        cursor.execute("SELECT * FROM sexual ORDER BY id DESC")
    
    results = cursor.fetchall()
    conn.close()
    return results

def get_sexual(entry_id: int) -> Optional[sqlite3.Row]:
    """Get a single sexual entry."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sexual WHERE id = ?", (entry_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_sexual_categories() -> List[sqlite3.Row]:
    """Get all sexual categories."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sexual_categories ORDER BY name")
    results = cursor.fetchall()
    conn.close()
    return results

def add_sexual_category(name: str) -> int:
    """Add a new sexual category."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sexual_categories (name) VALUES (?)", (name,))
    cat_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return cat_id

