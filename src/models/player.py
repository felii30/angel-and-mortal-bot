from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class Player:
    username: str
    chat_id: Optional[int] = None
    angel: Optional['Player'] = None
    mortal: Optional['Player'] = None

    @property
    def is_registered(self) -> bool:
        """Check if player has registered with the bot"""
        return self.chat_id is not None

class PlayerManager:
    def __init__(self):
        self.players: Dict[str, Player] = {}
    
    def add_player(self, username: str) -> Player:
        """Add a new player or get existing one"""
        username = username.lower()
        if username not in self.players:
            self.players[username] = Player(username=username)
        return self.players[username]
    
    def get_player(self, username: str) -> Optional[Player]:
        """Get a player by username"""
        return self.players.get(username.lower())
    
    def set_angel_mortal(self, player_username: str, angel_username: str, mortal_username: str) -> None:
        """Set up angel and mortal relationships"""
        player = self.get_player(player_username)
        angel = self.get_player(angel_username)
        mortal = self.get_player(mortal_username)
        
        if all([player, angel, mortal]):
            player.angel = angel
            player.mortal = mortal
    
    def validate_pairings(self) -> bool:
        """Validate that all angel/mortal pairings are correct"""
        for player in self.players.values():
            if not player.angel or not player.mortal:
                return False
            if (player.angel.mortal.username != player.username or 
                player.mortal.angel.username != player.username):
                return False
        return True 