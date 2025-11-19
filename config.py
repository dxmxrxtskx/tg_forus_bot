"""Configuration management for the bot."""
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CONFIG_FILE = BASE_DIR / "config.json"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables")

# Load user configuration
def load_config():
    """Load user configuration from config.json."""
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_FILE}")
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Validate users
    users = config.get('users', [])
    if len(users) < 2:
        raise ValueError("At least 2 users must be configured")
    
    # Validate each user has required fields
    for user in users:
        if 'telegram_id' not in user or 'display_name' not in user:
            raise ValueError("Each user must have 'telegram_id' and 'display_name'")
    
    return config

# Load config
try:
    CONFIG = load_config()
    USERS = CONFIG.get('users', [])
    USER_IDS = [user['telegram_id'] for user in USERS]
    USER_DISPLAY_NAMES = {user['telegram_id']: user['display_name'] for user in USERS}
except FileNotFoundError:
    # Config will be created by deploy script
    CONFIG = {}
    USERS = []
    USER_IDS = []
    USER_DISPLAY_NAMES = {}

def is_authorized_user(telegram_id: int) -> bool:
    """Check if user is authorized."""
    return telegram_id in USER_IDS

