import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Config:
    # Bot Token
    BOT_TOKEN = os.getenv("ANGEL_BOT_TOKEN")
    
    # File paths
    PLAYER_DATA_FILE = "data/players.csv"
    CHAT_ID_JSON = "data/chat_ids.json"
    LOG_DIR = 'logs'
    
    # Message icons/aliases
    ANGEL_ICON = "😇"
    MORTAL_ICON = "🙇"
    
    # Conversation states
    CHOOSING, ANGEL, MORTAL = range(3)
    
    @staticmethod
    def setup_directories():
        """Create necessary directories if they don't exist"""
        directories = ['logs', 'data']
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory) 