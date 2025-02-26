import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict

@dataclass
class RateLimit:
    max_requests: int
    time_window: int  # in seconds
    requests: list[float] = None

    def __post_init__(self):
        self.requests = []

class RateLimitService:
    def __init__(self):
        self.limits: Dict[str, RateLimit] = defaultdict(
            lambda: RateLimit(max_requests=5, time_window=60)  # Default: 5 messages per minute
        )
    
    def can_send_message(self, username: str) -> bool:
        """Check if user can send a message based on rate limits"""
        limit = self.limits[username]
        current_time = time.time()
        
        # Remove old requests outside the time window
        limit.requests = [t for t in limit.requests if current_time - t <= limit.time_window]
        
        # Check if user has exceeded rate limit
        if len(limit.requests) >= limit.max_requests:
            return False
        
        # Add new request
        limit.requests.append(current_time)
        return True
    
    def get_remaining_time(self, username: str) -> float:
        """Get remaining time until next message is allowed"""
        limit = self.limits[username]
        if len(limit.requests) < limit.max_requests:
            return 0
            
        current_time = time.time()
        oldest_request = min(limit.requests)
        return max(0, limit.time_window - (current_time - oldest_request))
    
    def set_limit(self, username: str, max_requests: int, time_window: int):
        """Set custom rate limit for a user"""
        self.limits[username] = RateLimit(max_requests=max_requests, time_window=time_window) 