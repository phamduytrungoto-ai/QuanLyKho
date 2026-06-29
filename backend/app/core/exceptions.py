"""Custom exceptions for the application."""

from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class DuplicateError(HTTPException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class InsufficientStockError(HTTPException):
    def __init__(self, detail: str = "Insufficient stock"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class PermissionDeniedError(HTTPException):
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class InvalidStateError(HTTPException):
    def __init__(self, detail: str = "Invalid state transition"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
