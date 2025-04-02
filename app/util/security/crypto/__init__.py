from .kdf_handler import KdfHandler
from .fernet_handler import FernetHandler

kdf = KdfHandler()
fernet = FernetHandler()

__all__ = ["kdf", "fernet"]