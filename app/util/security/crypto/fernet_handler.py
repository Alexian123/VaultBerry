from cryptography.fernet import Fernet
from .crypto_handler import CryptoHandler

class FernetHandler(CryptoHandler):
    
    def __init__(self, key: bytes):
        super().__init__(key)
        self._fernet = Fernet(key)
    
    def __init__(self):
        super().__init__()
        self._fernet = None
        
    def init(self, key: bytes):
        super().init(key)
        self._fernet = Fernet(key)
    
    def encrypt(self, data: bytes) -> bytes:
        if not self.is_initialized:
            raise ValueError("CryptoHandler is not initialized")
        return self._fernet.encrypt(data)
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        if not self.is_initialized:
            raise ValueError("CryptoHandler is not initialized")
        return self._fernet.decrypt(encrypted_data)