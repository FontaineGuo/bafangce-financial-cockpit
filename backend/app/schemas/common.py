"""
通用schemas
"""
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    """通用API响应"""
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    error: Optional[str] = None

    @classmethod
    def success_response(cls, data: T = None, message: str = "Success") -> "Response[T]":
        """成功响应"""
        return cls(success=True, data=data, message=message)

    @classmethod
    def error_response(cls, error: str, data: T = None) -> "Response[T]":
        """错误响应"""
        return cls(success=False, data=data, error=error)


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应"""
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int
