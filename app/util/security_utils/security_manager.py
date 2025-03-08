from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import secrets
import base64

class SecurityManager:
    
    @classmethod
    def generate_otp(digits=9):
        """Generates a random one-time password with digits."""
        return ''.join([str(secrets.randbelow(10)) for _ in range(digits)])
    
    @classmethod
    def generate_salt(length=16) -> bytes:
        """Generates a cryptographically secure random salt."""
        return secrets.token_bytes(length)
    
    @classmethod
    def generate_fernet_key() -> str:
        """Generates a Fernet key."""
        return Fernet.generate_key()
    
    @classmethod
    def generate_kdf_secret(length=32) -> str:
        """Generates a secret for key derivation."""
        return secrets.token_urlsafe(length)
    
    def __init__(self, fernet_key: str, kdf_secret: str, kdf_iterations=390000):
        """Initializes the SecurityManager with the Fernet key and KDF secret."""
        self._fernet = Fernet(fernet_key.encode())
        self._kdf_secret = kdf_secret
        self._kdf_iterations = kdf_iterations
        
    def __init__(self, kdf_iterations=390000):
        """Initializes the SecurityManager with the KDF iterations."""
        self._kdf_iterations = kdf_iterations
        
    def init(self, fernet_key: str, kdf_secret: str):
        """Initializes the SecurityManager with the Fernet key and KDF secret."""
        self._fernet = Fernet(fernet_key.encode())
        self._kdf_secret = kdf_secret

    def encrypt_data(self, data: bytes) -> bytes:
        """Encrypts data using Fernet."""
        return self._fernet.encrypt(data)
    
    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypts data using Fernet."""
        return self._fernet.decrypt(encrypted_data)
    
    def derive_key(self, secret: str, salt: bytes) -> bytes:
        """Derives a key from the secret and salt using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self._kdf_iterations,
            backend=default_backend()
        )
        derived_key = kdf.derive(secret.encode() + self._kdf_secret.encode())
        return derived_key
    
    def verify_kdf(self, derived_key: bytes, salt:bytes) -> bytes:
        """
            Verifies consistency of KDF parameters and computes and returns the secret
            for pyotp, base32 encoded.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self._kdf_iterations,
            backend=default_backend()
        )
        try:
            kdf.verify(derived_key, self._kdf_secret.encode()) # dummy verify
            return base64.b32encode(derived_key).decode('utf-8').rstrip('=')
        except:
            return None