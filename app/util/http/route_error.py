from .error_code import ErrorCode

class RouteError(Exception):
    """Custom exception class for handling HTTP errors.

    This exception allows associating a specific error message and an
    ErrorCode enum member with the error condition.

    Attributes:
        message (str): A human-readable description of the error that occurred.
        error_code (ErrorCode): An Enum member representing the error type.
    """

    def __init__(self, message: str, error_code: ErrorCode):
        """
        Initializes a new instance of the RouteError exception.

        Args:
            message (str): The detailed error message explaining the issue.
            error_code (ErrorCode): The specific ErrorCode enum member
                                    associated with this error.
        """
        # Ensure error_code is an instance of ErrorCode enum
        if not isinstance(error_code, ErrorCode):
            raise TypeError("error_code must be an instance of ErrorCode enum")

        # Call the base Exception class's initializer.
        # We use error_code.value to get the integer value for the message.
        super().__init__(f"Error Code {error_code.value} ({error_code.name}): {message}")

        # Store the custom message and the ErrorCode enum member
        self.message = message
        self.error_code = error_code # Store the enum member itself

    def __str__(self) -> str:
        """
        Returns a string representation of the exception
        """
        return f"{self.message}"