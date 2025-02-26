import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from src.config.config import Config

@dataclass
class UserProfile:
    username: str
    nickname: Optional[str] = None
    interests: List[str] = None
    bio: Optional[str] = None

    def __post_init__(self):
        if self.interests is None:
            self.interests = []

class ProfileService:
    def __init__(self):
        self.profiles_file = os.path.join(Config.DATA_DIR, 'user_profiles.json')
        self.profiles: Dict[str, UserProfile] = {}
        self.load_profiles()
    
    def load_profiles(self):
        """Load profiles from file"""
        try:
            if os.path.exists(self.profiles_file):
                with open(self.profiles_file, 'r') as f:
                    data = json.load(f)
                    self.profiles = {
                        username: UserProfile(**profile_data)
                        for username, profile_data in data.items()
                    }
        except Exception as e:
            print(f"Error loading profiles: {e}")
    
    def save_profiles(self):
        """Save profiles to file"""
        try:
            with open(self.profiles_file, 'w') as f:
                json.dump(
                    {username: asdict(profile) for username, profile in self.profiles.items()},
                    f,
                    indent=4
                )
        except Exception as e:
            print(f"Error saving profiles: {e}")
    
    def get_or_create_profile(self, username: str) -> UserProfile:
        """Get existing profile or create new one"""
        if username not in self.profiles:
            self.profiles[username] = UserProfile(username=username)
            self.save_profiles()
        return self.profiles[username]
    
    def set_nickname(self, username: str, nickname: str) -> bool:
        """Set user's nickname"""
        profile = self.get_or_create_profile(username)
        profile.nickname = nickname
        self.save_profiles()
        return True
    
    def add_interest(self, username: str, interest: str) -> bool:
        """Add an interest to user's profile"""
        profile = self.get_or_create_profile(username)
        if interest not in profile.interests:
            profile.interests.append(interest)
            self.save_profiles()
        return True
    
    def remove_interest(self, username: str, interest: str) -> bool:
        """Remove an interest from user's profile"""
        profile = self.get_or_create_profile(username)
        if interest in profile.interests:
            profile.interests.remove(interest)
            self.save_profiles()
        return True
    
    def set_bio(self, username: str, bio: str) -> bool:
        """Set user's bio"""
        profile = self.get_or_create_profile(username)
        profile.bio = bio
        self.save_profiles()
        return True
    
    def get_profile_summary(self, username: str) -> str:
        """Get a formatted summary of user's profile"""
        profile = self.get_or_create_profile(username)
        return (
            f"👤 Profile for {profile.nickname or username}:\n\n"
            f"Bio: {profile.bio or 'No bio set'}\n"
            f"Interests: {', '.join(profile.interests) or 'No interests added'}"
        )
    
    def get_full_profile_view(self, username: str, angel_username: str, mortal_username: str) -> str:
        """Get a complete view of user's profile along with angel and mortal profiles"""
        user_profile = self.get_or_create_profile(username)
        angel_profile = self.get_or_create_profile(angel_username)
        mortal_profile = self.get_or_create_profile(mortal_username)
        
        return (
            f"🎭 Your Profile:\n"
            f"Nickname: {user_profile.nickname or username}\n"
            f"Bio: {user_profile.bio or 'No bio set'}\n"
            f"Interests: {', '.join(user_profile.interests) or 'No interests added'}\n\n"
            f"👼 Your Angel's Profile:\n"
            f"Nickname: {angel_profile.nickname or '???'}\n"
            f"Bio: {angel_profile.bio or 'No bio set'}\n"
            f"Interests: {', '.join(angel_profile.interests) or 'No interests added'}\n\n"
            f"😇 Your Mortal's Profile:\n"
            f"Nickname: {mortal_profile.nickname or '???'}\n"
            f"Bio: {mortal_profile.bio or 'No bio set'}\n"
            f"Interests: {', '.join(mortal_profile.interests) or 'No interests added'}"
        ) 