from .crypto import fernet, kdf
from .password_hasher import PasswordHasher
from .token_generator import TokenGenerator

hasher = PasswordHasher()
generator = TokenGenerator()

__all__ = ["hasher", "generator", "fernet", "kdf"]