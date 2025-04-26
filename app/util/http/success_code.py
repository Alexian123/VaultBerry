import enum

class SuccessCode(enum.IntEnum):
    """Enumeration for standard HTTP status codes used for success responses."""
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204