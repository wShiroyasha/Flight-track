from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
ph = PasswordHasher()

def hash_password(password : str) -> str:
    return ph.hash(password)

def verify_password(password_entered : str, hashed_password : str) -> bool:
    try:
        return ph.verify(hashed_password, password_entered)
    except VerifyMismatchError:
        return False