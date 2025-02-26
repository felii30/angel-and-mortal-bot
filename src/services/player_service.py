import logging
from typing import Optional, Dict, Tuple
from src.models.player import Player, PlayerManager
from src.utils.database import DatabaseHandler

logger = logging.getLogger(__name__)

class PlayerService:
    def __init__(self, player_manager: PlayerManager, db_handler: DatabaseHandler):
        self.player_manager = player_manager
        self.db_handler = db_handler
        
    def initialize_data(self) -> bool:
        """Initialize player data from storage"""
        try:
            self.db_handler.load_players()
            self.db_handler.load_chat_ids()
            return True
        except Exception as e:
            logger.error(f"Failed to initialize player data: {e}")
            return False
    
    def register_player(self, username: str, chat_id: int) -> Optional[Player]:
        """Register a player with their chat ID"""
        player = self.player_manager.get_player(username)
        if not player:
            return None
            
        player.chat_id = chat_id
        self.db_handler.save_chat_ids()
        return player
    
    def get_player_relationships(self, username: str) -> Optional[Tuple[Player, Player]]:
        """Get a player's angel and mortal"""
        player = self.player_manager.get_player(username)
        if not player:
            return None
            
        return (player.angel, player.mortal)
    
    def is_registered(self, username: str) -> bool:
        """Check if a player is registered"""
        player = self.player_manager.get_player(username)
        return player is not None 