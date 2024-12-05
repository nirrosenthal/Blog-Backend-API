
class BlogAppException(Exception):
    """Exception wrapper of the Application"""
    def __init__(self, message:str, error_code:int):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class ResourceNotFoundError(BlogAppException):
    """Raised when a resource is not found"""
    def __init__(self, message="Resource not found"):
        self.message = message
        self.error_code = 404
        super().__init__(self.message, self.error_code)

class InputValidationError(BlogAppException):
    """Raised for input validation failures"""
    def __init__(self, message="Validation failed"):
        self.message = message
        self.error_code=400
        super().__init__(self.message, self.error_code)

class DatabaseError(BlogAppException):
    """Raised when there is a database-related error"""
    def __init__(self, message="Database error occurred"):
        self.message = message
        self.error_code = 500
        super().__init__(self.message, self.error_code)


class AuthenticationError(BlogAppException):
    """Raise when there is an error with the authentication process"""
    def __init__(self, message="Authentication Failed"):
        self.message = message
        self.error_code = 401
        super().__init__(self.message, self.error_code)


class UnauthorizedError(BlogAppException):
    """Raised when a user is not authorized to access a resource"""
    def __init__(self, message="Unauthorized access"):
        self.message = message
        self.error_code = 401
        super().__init__(self.message, self.error_code)

class ForbiddenError(BlogAppException):
    """Raised when a known user is not unauthorized for this action"""
    def __init__(self, message="Unauthorized access"):
        self.message = message
        self.error_code = 403
        super().__init__(self.message, self.error_code)

class TimeoutError(BlogAppException):
    """Raised when the timeout for a request has passed"""
    def __init__(self, message="Timeout passed"):
        self.message = message
        self.error_code = 408
        super().__init__(self.message, self.error_code)