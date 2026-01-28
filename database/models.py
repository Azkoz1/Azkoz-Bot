"""
Database models and operations
"""

from datetime import datetime
from typing import Optional, List

class UserWarning:
    """Model for user warnings"""
    
    def __init__(self, user_id: int, guild_id: int, reason: str, moderator_id: int):
        self.user_id = user_id
        self.guild_id = guild_id
        self.reason = reason
        self.moderator_id = moderator_id
        self.timestamp = datetime.utcnow()
    
    def __repr__(self):
        return f"<UserWarning user_id={self.user_id} reason='{self.reason}'>"

class BroadcastLog:
    """Model for broadcast logs"""
    
    def __init__(self, guild_id: int, message: str, target: str, count: int):
        self.guild_id = guild_id
        self.message = message
        self.target = target  # 'channels', 'users', 'roles'
        self.count = count
        self.timestamp = datetime.utcnow()
    
    def __repr__(self):
        return f"<BroadcastLog guild_id={self.guild_id} target={self.target} count={self.count}>"

class GuildConfig:
    """Model for guild configuration"""
    
    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        self.welcome_channel_id: Optional[int] = None
        self.log_channel_id: Optional[int] = None
        self.mod_role_id: Optional[int] = None
        self.prefix = "!"
        self.auto_mod_enabled = True
        self.created_at = datetime.utcnow()
    
    def __repr__(self):
        return f"<GuildConfig guild_id={self.guild_id}>"

# In-memory storage (replace with database in production)
class DataStore:
    """Simple in-memory data storage"""
    
    def __init__(self):
        self.warnings: List[UserWarning] = []
        self.broadcasts: List[BroadcastLog] = []
        self.guild_configs: dict = {}
    
    def add_warning(self, warning: UserWarning):
        """Add a warning"""
        self.warnings.append(warning)
    
    def get_user_warnings(self, user_id: int, guild_id: int) -> int:
        """Get warning count for user"""
        return sum(1 for w in self.warnings 
                  if w.user_id == user_id and w.guild_id == guild_id)
    
    def clear_warnings(self, user_id: int, guild_id: int):
        """Clear warnings for user"""
        self.warnings = [w for w in self.warnings 
                        if not (w.user_id == user_id and w.guild_id == guild_id)]
    
    def log_broadcast(self, broadcast: BroadcastLog):
        """Log a broadcast"""
        self.broadcasts.append(broadcast)
    
    def get_guild_config(self, guild_id: int) -> GuildConfig:
        """Get or create guild config"""
        if guild_id not in self.guild_configs:
            self.guild_configs[guild_id] = GuildConfig(guild_id)
        return self.guild_configs[guild_id]

# Global data store instance
data_store = DataStore()
