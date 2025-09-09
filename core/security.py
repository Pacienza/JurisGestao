from __future__ import annotations
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

def hash_password(plain: str) -> str:
    return ph.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return ph.verify(hashed, plain)
    except VerifyMismatchError:
        return False
