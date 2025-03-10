from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import secrets

class SecurityManager:
    
    @classmethod
    def generate_otp(cls, length=9):
        """Generate a random one-time numeric password.

        Args:
            length (int, optional): The length of the password. Defaults to 9.

        Returns:
            str: The generated one-time password.
        """
        return ''.join([str(secrets.randbelow(10)) for _ in range(length)])
    
    @classmethod
    def generate_salt(cls, length=16) -> bytes:
        """Generates a cryptographically secure random salt.

        Args:
            length (int, optional): The length of the salt. Defaults to 16.

        Returns:
            bytes: The generated salt.
        """
        return secrets.token_bytes(length)
    
    @classmethod
    def generate_fernet_key(cls) -> bytes:
        """Generates a Fernet key.

        Returns:
            bytes: The fernet encryption/decryption key.
        """
        return Fernet.generate_key()
    
    @classmethod
    def generate_kdf_secret(cls, length=32) -> str:
        """Generates a secret for key derivation.

        Args:
            length (int, optional): The length of the secret. Defaults to 32.

        Returns:
            str: The kdf secret as a URL-safe string.
        """
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
        """Encrypts data using Fernet.

        Args:
            data (bytes): Data to be encrypted.

        Returns:
            bytes: Encrypted data.
        """
        return self._fernet.encrypt(data)
    
    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypts data using Fernet.

        Args:
            encrypted_data (bytes): Data to be decrypted.

        Returns:
            bytes: Decrypted data.
        """
        return self._fernet.decrypt(encrypted_data)
    
    def derive_key(self, secret: str, salt: bytes) -> bytes:
        """Derives a key from the secret and salt using PBKDF2.

        Args:
            secret (str): Secret for derivation.
            salt (bytes): Random salt.

        Returns:
            bytes: The derived key.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self._kdf_iterations,
            backend=default_backend()
        )
        derived_key = kdf.derive(secret.encode() + self._kdf_secret.encode())
        return derived_key