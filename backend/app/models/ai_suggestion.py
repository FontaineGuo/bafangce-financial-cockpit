"""
AI建议数据模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ..core.database import Base
from .enums import AISuggestionType, AISuggestionPriority, AISuggestionStatus


class AISuggestion(Base):
    """AI建议表"""
    __tablename__ = "ai_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False, index=True, comment="投资组合ID")
    type = Column(String(20), nullable=False, comment="建议类型")
    title = Column(String(200), nullable=False, comment="建议标题")
    content = Column(Text, nullable=False, comment="建议内容")
    priority = Column(String(10), nullable=False, comment="优先级")
    status = Column(String(20), default="pending", comment="状态")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    applied_at = Column(DateTime, comment="应用时间")

    def __repr__(self):
        return f"<AISuggestion {self.title}>"
