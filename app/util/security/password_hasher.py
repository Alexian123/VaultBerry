import werkzeug.security as wz_security

class PasswordHasher:

    @staticmethod
    def hash(password: str) -> str:
        """Hashes a password using the werkzeug security module.

        Args:
            password (str): The password to hash.

        Returns:
            str: The hashed password.
        """
        return wz_security.generate_password_hash(password)

    @staticmethod
    def check(password_hash: str, password: str) -> bool:
        """Checks if a password matches its hash.

        Args:
            password_hash (str): The hash to check against.
            password (str): The password to check.

        Returns:
            bool: True if the password matches the hash, False otherwise.
        """
        return wz_security.check_password_hash(password_hash, password)