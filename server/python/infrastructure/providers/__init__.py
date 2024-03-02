import string
import secrets

from typing import Optional
from domain.providers import PasswordHasher
from hashlib import md5, sha512

PASSWORD_HASHER_PROVIDERS = {
    'MD5': lambda: MD5PasswordHasher(),
    'SALT_SHA512': lambda: SaltSHA512PasswordHasher(),
}


class MD5PasswordHasher(PasswordHasher):
    """
    MD5 Password Hasher implementation
    """
    def do_verify(self, password: str, hashed_password: bytes) -> bool:
        return md5(password.encode()).digest() == hashed_password

    def do_hash(self, password: str) -> bytes:
        return md5(password.encode()).digest()


class SaltSHA512PasswordHasher(PasswordHasher):
    """
    SHA512 Password Hasher implementation using SALT
    """

    @staticmethod
    def _create_salt(length: int = 10) -> str:
        base = string.ascii_letters + string.digits
        return ''.join([secrets.choice(base) for _ in range(length)])

    def do_verify(self, password: str, hashed_password: bytes) -> bool:
        (salt, _) = hashed_password.decode().split('$')
        return self.do_hash(password, salt) == hashed_password

    def do_hash(self, password: str, salt: Optional[str] = None) -> bytes:
        if salt is None:
            salt = self._create_salt()
        password_hashed = sha512((password + salt).encode()).hexdigest()

        return (salt + '$' + password_hashed).encode()
