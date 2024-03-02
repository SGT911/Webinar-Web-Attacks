from __future__ import annotations
import domain.errors as err
from typing import Optional, Union, TypeVar, Generic
from abc import ABC, abstractmethod
import re

from domain.providers import PasswordHasher

_user_name_pattern = re.compile(r'^[A-Z_][A-Z0-9\-_.]+[A-Z0-9_]$', re.IGNORECASE)
T = TypeVar('T')


class Exporter(Generic[T], ABC):
    """
    Abstract implementation of exporter interface
    """

    @abstractmethod
    def export(self) -> T:
        """
        Export into a serializable instance of the model

        **NOTE:** Export and load a model may occur into data loss
        :return: Serializable instance
        """
        raise NotImplementedError()

    @abstractmethod
    def load(self, data: T) -> Exporter:
        """
        Load a serializable instance of the model into the model
        :param data: Serializable instance
        :return: Model instance
        """
        raise NotImplementedError()


class User(Exporter[dict]):
    """
    User model
    """

    def __init__(self, user_name: str, full_name: str, password: Optional[Union[str, bytes]] = None):
        assert 4 <= len(user_name) <= 16, err.LENGTH_NOT_VALID.format(field='user_name', min=4, max=16)
        assert _user_name_pattern.match(user_name) is not None, \
            err.PATTERN_NOT_VALID.format(field='user_name', pattern=_user_name_pattern)
        self.user_name = user_name.upper()

        assert len(full_name) != 0, err.EMPTY.format(field='full_name')
        self.full_name = full_name.lower()

        if password is not None:
            if isinstance(password, bytes):
                self.password = password
            else:
                assert len(password) != 0, err.EMPTY.format(field='password')
                assert 8 <= len(password), err.LENGTH_NOT_VALID.format(field='password', min=8, max=10e10)
                self.password = PasswordHasher.hash(password)

    def load(self, data: dict) -> User:
        return User(data['username'], data['full_name'])

    def export(self) -> dict:
        return dict(user_name=self.user_name, full_name=self.full_name)

    def set_password(self, new_password: str, password: str):
        """
        Set a new password ensuring the old one
        :param new_password: Password to change
        :param password: Old password validation
        """

        assert len(new_password) != 0, err.EMPTY.format(field='new_password')
        assert 8 <= len(new_password), err.LENGTH_NOT_VALID.format(field='new_password', min=8, max=10e10)
        assert new_password != password, err.EQUALS.format(field='password')
        assert self.verify_password(password), err.INVALID_CREDENTIAL

        self.password = PasswordHasher.hash(new_password)

    def verify_password(self, password: str) -> bool:
        """
        Verify the user password from the model store

        :exception RuntimeError: If password is not stored in the model
        :param password: Test password
        :return: Validity
        """
        if self.password is None:
            raise RuntimeError('password should be provided')

        return PasswordHasher.verify(password, self.password)

    def __repr__(self) -> str:
        return '<User({user_name!s}, {full_name!r})>'.format(user_name=self.user_name, full_name=self.full_name.title())