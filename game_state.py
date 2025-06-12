"""
Game State - Represents the state of a single game instance
"""

import random
from typing import Dict, List, Optional
from dataclasses import dataclass
from config import ROLES

@dataclass
class Player:
    """Represents a player in the game"""
    user_id: int
    username: str
    role: str = ""
    is_rat: bool = False
    alive: bool = True

class GameState:
    """Represents the state of a single game"""
    
    def __init__(self, chat_id: int, creator_id: int, creator_username: str):
        self.chat_id = chat_id
        self.creator_id = creator_id
        self.phase = "registration"  # registration, discussion, voting, ended
        self.players: Dict[int, Player] = {}
        self.votes: Dict[int, int] = {}  # voter_id -> target_id
        self.round_number = 1
        
        # Add creator as first player
        self.add_player(creator_id, creator_username)
    
    def add_player(self, user_id: int, username: str) -> bool:
        """Add a player to the game"""
        if user_id in self.players:
            return False
        
        self.players[user_id] = Player(user_id, username)
        return True
    
    def assign_roles(self):
        """Randomly assign roles to players, including the rat"""
        player_list = list(self.players.values())
        available_roles = ROLES.copy()
        
        # Randomly select one player to be the rat
        rat_player = random.choice(player_list)
        rat_player.is_rat = True
        
        # Assign random roles to all players
        random.shuffle(available_roles)
        for i, player in enumerate(player_list):
            if i < len(available_roles):
                player.role = available_roles[i]
            else:
                # If more players than roles, cycle through roles
                player.role = available_roles[i % len(available_roles)]
    
    def start_discussion(self):
        """Start the discussion phase"""
        self.phase = "discussion"
        self.votes.clear()
    
    def start_voting(self):
        """Start the voting phase"""
        self.phase = "voting"
    
    def end_game(self):
        """End the game"""
        self.phase = "ended"
    
    def all_votes_cast(self) -> bool:
        """Check if all alive players have voted"""
        alive_players = [p for p in self.players.values() if p.alive]
        return len(self.votes) >= len(alive_players)
    
    def get_alive_players(self) -> List[Player]:
        """Get list of alive players"""
        return [p for p in self.players.values() if p.alive]
    
    def get_rat_player(self) -> Optional[Player]:
        """Get the rat player"""
        for player in self.players.values():
            if player.is_rat:
                return player
        return None
