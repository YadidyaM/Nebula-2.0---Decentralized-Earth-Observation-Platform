from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class UserRole(str, Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"
    RESEARCHER = "researcher"

class NotificationType(str, Enum):
    MISSION_UPDATE = "mission_update"
    AGENT_STATUS = "agent_status"
    RISK_ALERT = "risk_alert"
    SYSTEM_ALERT = "system_alert"
    REWARD_CLAIM = "reward_claim"

class ThemePreference(str, Enum):
    CYAN = "cyan"
    PURPLE = "purple"
    GREEN = "green"
    AMBER = "amber"

class UserSettings(BaseModel):
    """User preferences and settings"""
    theme: ThemePreference = ThemePreference.CYAN
    notifications_enabled: bool = True
    notification_types: List[NotificationType] = [
        NotificationType.MISSION_UPDATE,
        NotificationType.RISK_ALERT,
        NotificationType.SYSTEM_ALERT
    ]
    preferred_agents: List[str] = []
    api_preferences: Dict[str, Any] = {
        "auto_refresh": True,
        "refresh_interval": 30,
        "data_retention_days": 30
    }
    dashboard_layout: Dict[str, Any] = {
        "panels": ["missions", "agents", "telemetry"],
        "panel_order": ["missions", "agents", "telemetry", "blockchain"],
        "default_panel": "missions"
    }
    voice_settings: Dict[str, Any] = {
        "enabled": False,
        "language": "en-US",
        "voice_model": "default"
    }
    performance_settings: Dict[str, Any] = {
        "fps_limit": 60,
        "quality": "high",
        "animations_enabled": True
    }

class WalletAddress(BaseModel):
    """Wallet address information"""
    address: str
    network: str = "mainnet"  # mainnet, devnet, testnet
    is_primary: bool = False
    added_at: datetime = Field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    balance_sol: float = 0.0
    balance_nebula: float = 0.0

class ActivityEntry(BaseModel):
    """User activity log entry"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    activity_type: str
    description: str
    metadata: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class UserProfile(BaseModel):
    """Complete user profile schema"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: UserRole = UserRole.VIEWER
    
    # Authentication
    password_hash: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    verification_token: Optional[str] = None
    
    # Wallet management
    primary_wallet: Optional[str] = None
    wallet_addresses: List[WalletAddress] = []
    
    # User settings
    settings: UserSettings = Field(default_factory=UserSettings)
    
    # Activity tracking
    created_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    login_count: int = 0
    
    # Mission and reward tracking
    missions_created: int = 0
    missions_participated: int = 0
    total_rewards: float = 0.0
    rewards_claimed: float = 0.0
    
    # Activity history
    activity_history: List[ActivityEntry] = []
    
    # API usage tracking
    api_calls_today: int = 0
    api_calls_total: int = 0
    last_api_call: Optional[datetime] = None
    
    # Preferences
    timezone: str = "UTC"
    language: str = "en"
    country: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = {}

class UserCreate(BaseModel):
    """Schema for creating a new user"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.VIEWER
    primary_wallet: Optional[str] = None
    timezone: str = "UTC"
    language: str = "en"
    country: Optional[str] = None

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    settings: Optional[UserSettings] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    country: Optional[str] = None

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str
    remember_me: bool = False

class UserPasswordChange(BaseModel):
    """Schema for password change"""
    current_password: str
    new_password: str = Field(..., min_length=8)

class UserPasswordReset(BaseModel):
    """Schema for password reset request"""
    email: EmailStr

class UserPasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8)

class WalletAdd(BaseModel):
    """Schema for adding a wallet address"""
    address: str
    network: str = "mainnet"
    is_primary: bool = False

class WalletUpdate(BaseModel):
    """Schema for updating wallet information"""
    address: str
    network: Optional[str] = None
    is_primary: Optional[bool] = None

class UserStats(BaseModel):
    """User statistics for dashboard"""
    total_missions: int
    active_missions: int
    completed_missions: int
    total_rewards: float
    rewards_claimed: float
    rewards_pending: float
    api_calls_today: int
    api_calls_total: int
    login_streak: int
    last_login: Optional[datetime]
    account_age_days: int
    preferred_agents: List[str]
    most_active_hour: Optional[int]

class UserActivitySummary(BaseModel):
    """Summary of user activity"""
    period: str  # "today", "week", "month", "year"
    missions_created: int
    missions_participated: int
    api_calls: int
    rewards_earned: float
    most_active_day: Optional[str]
    most_used_feature: Optional[str]
    activity_trend: str  # "increasing", "decreasing", "stable"

# Query helper functions (these would be implemented in the service layer)
class UserQueryHelpers:
    """Helper functions for user queries"""
    
    @staticmethod
    def by_wallet(wallet_address: str) -> Dict[str, Any]:
        """Query filter for finding user by wallet address"""
        return {
            "$or": [
                {"primary_wallet": wallet_address},
                {"wallet_addresses.address": wallet_address}
            ]
        }
    
    @staticmethod
    def active_users() -> Dict[str, Any]:
        """Query filter for active users"""
        return {
            "is_active": True,
            "last_activity": {"$gte": datetime.now() - timedelta(days=30)}
        }
    
    @staticmethod
    def with_missions() -> Dict[str, Any]:
        """Query filter for users with missions"""
        return {
            "$or": [
                {"missions_created": {"$gt": 0}},
                {"missions_participated": {"$gt": 0}}
            ]
        }
    
    @staticmethod
    def by_role(role: UserRole) -> Dict[str, Any]:
        """Query filter for users by role"""
        return {"role": role.value}
    
    @staticmethod
    def verified_users() -> Dict[str, Any]:
        """Query filter for verified users"""
        return {"is_verified": True}
    
    @staticmethod
    def recent_activity(hours: int = 24) -> Dict[str, Any]:
        """Query filter for users with recent activity"""
        return {
            "last_activity": {"$gte": datetime.now() - timedelta(hours=hours)}
        }
    
    @staticmethod
    def high_reward_users(min_rewards: float = 100.0) -> Dict[str, Any]:
        """Query filter for high reward users"""
        return {"total_rewards": {"$gte": min_rewards}}
    
    @staticmethod
    def api_heavy_users(min_calls: int = 1000) -> Dict[str, Any]:
        """Query filter for API heavy users"""
        return {"api_calls_total": {"$gte": min_calls}}

# Index suggestions for MongoDB
class UserIndexes:
    """Suggested MongoDB indexes for user collection"""
    
    INDEXES = [
        # Primary lookups
        {"keys": [("email", 1)], "unique": True},
        {"keys": [("username", 1)], "unique": True},
        {"keys": [("primary_wallet", 1)]},
        {"keys": [("wallet_addresses.address", 1)]},
        
        # Activity and status
        {"keys": [("is_active", 1), ("last_activity", -1)]},
        {"keys": [("role", 1)]},
        {"keys": [("is_verified", 1)]},
        
        # Rewards and missions
        {"keys": [("total_rewards", -1)]},
        {"keys": [("missions_created", -1)]},
        {"keys": [("missions_participated", -1)]},
        
        # API usage
        {"keys": [("api_calls_total", -1)]},
        {"keys": [("api_calls_today", -1)]},
        
        # Time-based queries
        {"keys": [("created_at", -1)]},
        {"keys": [("last_login", -1)]},
        
        # Compound indexes
        {"keys": [("is_active", 1), ("role", 1)]},
        {"keys": [("is_active", 1), ("total_rewards", -1)]},
        {"keys": [("role", 1), ("last_activity", -1)]},
        
        # Activity history
        {"keys": [("activity_history.timestamp", -1)]},
        {"keys": [("activity_history.activity_type", 1)]},
        
        # Settings
        {"keys": [("settings.theme", 1)]},
        {"keys": [("settings.notifications_enabled", 1)]},
        
        # Text search
        {"keys": [("username", "text"), ("email", "text")]}
    ]
