from typing import Optional
from domain.providers import PasswordHasher
from hashlib import md5, sha512

from infrastructure.utils import create_salt

PASSWORD_HASHER_PROVIDERS = {
    'NULL': lambda: NullPasswordHasher(),
    'MD5': lambda: MD5PasswordHasher(),
    'SALT_SHA512': lambda: SaltSHA512PasswordHasher(),
}


class NullPasswordHasher(PasswordHasher):
    """
    Null implementation of PasswordHasher
    **IMPORTANT**: This password hasher does not encrypt any password
    """

    def do_verify(self, password: str, hashed_password: bytes) -> bool:
        return self.do_hash(password) == hashed_password

    def do_hash(self, password: str) -> bytes:
        return password.encode()


class MD5PasswordHasher(PasswordHasher):
    """
    MD5 Password Hasher implementation
    """
    def do_verify(self, password: str, hashed_password: bytes) -> bool:
        return self.do_hash(password) == hashed_password

    def do_hash(self, password: str) -> bytes:
        return md5(password.encode()).digest()


class SaltSHA512PasswordHasher(PasswordHasher):
    """
    SHA512 Password Hasher implementation using SALT
    """

    def do_verify(self, password: str, hashed_password: bytes) -> bool:
        (salt, _) = hashed_password.decode().split('$')
        return self.do_hash(password, salt) == hashed_password

    def do_hash(self, password: str, salt: Optional[str] = None) -> bytes:
        if salt is None:
            salt = create_salt()
        password_hashed = sha512((password + salt).encode()).hexdigest()

        return (salt + '$' + password_hashed).encode()
