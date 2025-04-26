import enum

class ErrorCode(enum.IntEnum):
    """Enumeration for standard HTTP status codes used in RouteError."""
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    INTERNAL_SERVER_ERROR = 500