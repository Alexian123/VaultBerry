from abc import ABC, abstractmethod

class CryptoHandler(ABC):
    
    def __init__(self, key: bytes):
        """Initializes the CryptoHandler with the encryption/decryption key."""
        if key is None or not isinstance(key, bytes):
            raise TypeError("Key must be bytes.")
        self.key = key
        self.is_initialized = True
        
    def __init__(self):
        """Initializes the CryptoHandler without the encryption/decryption key."""
        self.key = None
        self.is_initialized = False
        
    def init(self, key: bytes):
        """Initializes the CryptoHandler with the encryption/decryption key."""
        if key is None or not isinstance(key, bytes):
            raise TypeError("Key must be bytes.")
        self.key = key
        self.is_initialized = True
    
    @abstractmethod
    def encrypt(self, data: bytes) -> bytes:
        """Encrypts data.

        Args:
            key (bytes): The encryption/decryption key.
            data (bytes): Data to be encrypted.

        Returns:
            bytes: Encrypted data.
        """
        pass
   
    @abstractmethod
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """Decrypts data.

        Args:
            key (bytes): The encryption/decryption key.
            encrypted_data (bytes): Data to be decrypted.

        Returns:
            bytes: Decrypted data.
        """
        pass