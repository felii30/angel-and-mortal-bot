import json
import csv
import logging
from typing import Dict
from src.config.config import Config
from src.models.player import PlayerManager, Player

logger = logging.getLogger(__name__)

class DatabaseHandler:
    def __init__(self, player_manager: PlayerManager):
        self.player_manager = player_manager
        
    def load_players(self) -> None:
        """Load players from CSV file"""
        try:
            with open(Config.PLAYER_DATA_FILE) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                rows = list(csv_reader)
                
                # First pass: Create all players
                for i, row in enumerate(rows):
                    if i == 0:  # Skip header
                        continue
                    self.player_manager.add_player(row[0].strip())
                
                # Second pass: Set up relationships
                for i, row in enumerate(rows):
                    if i == 0:
                        continue
                    self.player_manager.set_angel_mortal(
                        row[0].strip(),
                        row[1].strip(),
                        row[2].strip()
                    )
                
                if not self.player_manager.validate_pairings():
                    raise ValueError("Invalid angel/mortal pairings detected")
                
                logger.info(f'Processed {len(rows) - 1} players.')
        except FileNotFoundError:
            logger.error(f"Players file not found: {Config.PLAYER_DATA_FILE}")
            raise
    
    def load_chat_ids(self) -> None:
        """Load chat IDs from JSON file"""
        try:
            with open(Config.CHAT_ID_JSON, 'r') as f:
                chat_ids = json.load(f)
                for username, chat_id in chat_ids.items():
                    player = self.player_manager.get_player(username)
                    if player:
                        player.chat_id = chat_id
                logger.info(f"Chat IDs loaded: {chat_ids}")
        except FileNotFoundError:
            logger.warning('Chat ID JSON file not found, creating new file.')
            self.save_chat_ids()
    
    def save_chat_ids(self) -> None:
        """Save chat IDs to JSON file"""
        chat_ids = {
            player.username: player.chat_id
            for player in self.player_manager.players.values()
            if player.chat_id is not None
        }
        
        with open(Config.CHAT_ID_JSON, 'w') as f:
            json.dump(chat_ids, f, indent=4)
        logger.info("Chat IDs saved successfully.") 