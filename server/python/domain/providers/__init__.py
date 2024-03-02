from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional


class PasswordHasher(ABC):
    """
    Password hasher provider and implementation abstract base class
    """
    _provided_hasher: Optional[PasswordHasher] = None

    @classmethod
    def provide_hasher(cls, provider: PasswordHasher):
        """
        Set globally an instance of the password hasher provider
        :param provider: Password hasher implementation
        """

        cls._provided_hasher = provider

    @classmethod
    def hash(cls, password: str) -> bytes:
        """
        Make a password hash
        :exception NotImplementedError: Password hasher not provided
        :param password: Unencrypted password
        :return: Encrypted password version
        """

        if cls._provided_hasher is None:
            raise NotImplementedError()

        return cls._provided_hasher.do_hash(password)

    @abstractmethod
    def do_hash(self, password: str) -> bytes:
        """
        Implementation of ``PasswordHasher.hash``
        :param password: Unencrypted password
        :return: Encrypted password version
        """

        raise NotImplementedError()

    @classmethod
    def verify(cls, password: str, hashed_password: bytes) -> bool:
        """
        Verify a password with the hashed version
        :exception NotImplementedError: Password hasher not provided
        :param password: Unencrypted password
        :param hashed_password: Provided password to test
        :return: Password validity
        """

        if cls._provided_hasher is None:
            raise NotImplementedError()

        return cls._provided_hasher.do_verify(password, hashed_password)

    @abstractmethod
    def do_verify(self, password: str, hashed_password: bytes) -> bool:
        """
        Implementation of ``PasswordHasher.verify``
        :param password: Unencrypted password
        :param hashed_password: Provided password to test
        :return: Password validity
        """
        raise NotImplementedError()
