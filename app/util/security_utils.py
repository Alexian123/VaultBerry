from werkzeug.security import generate_password_hash, check_password_hash
import secrets

def generate_otp(digits=9):
    return ''.join([str(secrets.randbelow(10)) for _ in range(digits)])