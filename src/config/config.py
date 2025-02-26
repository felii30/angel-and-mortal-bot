import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Config:
    # Bot Token
    BOT_TOKEN = os.getenv("ANGEL_BOT_TOKEN")
    
    # Base directories
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
    
    # Data files
    PLAYER_DATA_FILE = os.path.join(DATA_DIR, 'players.csv')
    CHAT_ID_JSON = os.path.join(DATA_DIR, 'chat_ids.json')
    
    # Message icons/aliases
    ANGEL_ICON = "😇"
    MORTAL_ICON = "🙇"
    
    # Conversation states
    CHOOSING, ANGEL, MORTAL = range(3)
    
    @staticmethod
    def setup_directories():
        """Create necessary directories if they don't exist"""
        directories = [Config.LOG_DIR, Config.DATA_DIR]
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory) 