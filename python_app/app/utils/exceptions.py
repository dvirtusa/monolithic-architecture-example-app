from typing import Optional


class AppException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        detail: Optional[str] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail or message
        super().__init__(self.message)


class UserAlreadyExistsException(AppException):
    def __init__(self, email: str):
        super().__init__(
            message=f"User with email '{email}' already exists",
            status_code=409,
            detail="A user with this email address is already registered",
        )


class UserNotFoundException(AppException):
    def __init__(self, identifier: str):
        super().__init__(
            message=f"User '{identifier}' not found",
            status_code=404,
            detail="User not found",
        )


class InvalidCredentialsException(AppException):
    def __init__(self):
        super().__init__(
            message="Invalid email or password",
            status_code=401,
            detail="The email or password you entered is incorrect",
        )


class DatabaseException(AppException):
    def __init__(self, operation: str, detail: Optional[str] = None):
        super().__init__(
            message=f"Database error during {operation}",
            status_code=500,
            detail=detail or "An unexpected database error occurred",
        )
