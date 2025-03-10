from werkzeug.security import generate_password_hash, check_password_hash
from .security_manager import SecurityManager

# Object for security related operations
manager = SecurityManager()