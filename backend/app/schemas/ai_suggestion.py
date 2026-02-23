"""
AI建议相关schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AISuggestion(BaseModel):
    """AI建议"""
    id: int
    portfolio_id: int
    type: str
    title: str
    content: str
    priority: str
    status: str = "pending"
    created_at: datetime
    applied_at: Optional[datetime] = None

    class Config:
        from_attributes = True
