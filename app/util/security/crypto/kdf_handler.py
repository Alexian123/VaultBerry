from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

class KdfHandler:
    
    def __init__(self):
        self.is_initialized = False
        self.secret = None
        self.iterations = None
        
    def init(self, secret: bytes, iterations=390000):
        """Initializes the KdfHandler with the KDF secret and iterations count."""
        if secret is not None and not isinstance(secret, bytes):
            raise TypeError("Secret must be bytes.")
        self.secret = secret
        self.iterations = iterations
        self.is_initialized = True
        
    def derive_key(self, password: bytes, salt: bytes) -> bytes:
        """Derives a key from the password and salt using PBKDF2.

        Args:
            password (bytes): Password for derivation.
            salt (bytes): Random salt.

        Returns:
            bytes: The derived key.
        """
        
        if password is not None and not isinstance(password, bytes):
            raise TypeError("Password must be bytes.")
        
        if salt is not None and not isinstance(salt, bytes):
            raise TypeError("Salt must be bytes.")
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.iterations,
            backend=default_backend()
        )
        derived_key = kdf.derive(password + self.secret)
        return derived_key