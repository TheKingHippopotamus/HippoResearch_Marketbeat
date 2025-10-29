"""
Result type for operations that can fail
Type בטוח לפעולות שיכולות להיכשל
"""
from typing import Generic, TypeVar, Optional
from dataclasses import dataclass

T = TypeVar('T')


@dataclass
class Result(Generic[T]):
    """
    Result type that can represent success or failure
    Type שמתאר תוצאה - הצלחה או כישלון
    
    Usage:
        result = some_operation()
        if result.is_ok():
            data = result.data
        else:
            error = result.error
    """
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    
    @classmethod
    def ok(cls, data: T) -> 'Result[T]':
        """Create a successful result"""
        return cls(success=True, data=data)
    
    @classmethod
    def err(cls, error: str) -> 'Result[T]':
        """Create a failed result"""
        return cls(success=False, error=error)
    
    def is_ok(self) -> bool:
        """Check if result is successful"""
        return self.success
    
    def is_err(self) -> bool:
        """Check if result is an error"""
        return not self.success
    
    def unwrap(self) -> T:
        """Get the data, raise exception if result is error"""
        if not self.success:
            raise ValueError(f"Attempted to unwrap error result: {self.error}")
        return self.data
    
    def unwrap_or(self, default: T) -> T:
        """Get the data, or return default if error"""
        return self.data if self.success else default

