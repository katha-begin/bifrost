"""
User domain models for the Bifrost system.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, EmailStr, Field


class UserPreferences(BaseModel):
    """User preferences configuration."""
    theme: str = Field(default="system", pattern="^(dark|light|system)$")
    language: str = Field(default="en")
    notifications_enabled: bool = Field(default=True)


class TeamMembership(BaseModel):
    """Team membership with role information."""
    team_id: UUID
    role: Optional[str] = None


class User(BaseModel):
    """Core user model representing a system user."""
    id: UUID = Field(default_factory=uuid4)
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password_hash: Optional[str] = None
    full_name: Optional[str] = None
    department: Optional[str] = None
    active: bool = Field(default=True)
    roles: List[str] = Field(default_factory=list)
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    teams: List[TeamMembership] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    """Model for creating a new user."""
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = None
    department: Optional[str] = None
    roles: List[str] = Field(default_factory=list)
    preferences: Optional[UserPreferences] = None
    teams: List[TeamMembership] = Field(default_factory=list)


class UserUpdate(BaseModel):
    """Model for updating an existing user."""
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(min_length=8, default=None)
    full_name: Optional[str] = None
    department: Optional[str] = None
    active: Optional[bool] = None
    roles: Optional[List[str]] = None
    preferences: Optional[UserPreferences] = None
    teams: Optional[List[TeamMembership]] = None
    metadata: Optional[Dict[str, Any]] = None