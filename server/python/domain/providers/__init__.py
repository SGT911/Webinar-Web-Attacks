from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Union, Literal


class PasswordHasher(ABC):
    """
    Password hasher provider and implementation abstract base class
    """
    _provided_hasher: Optional[PasswordHasher] = None

    target_key: str = 'not_implemented'

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


class FormSecurityProvider(ABC):
    """
    HTML Injector and validator for forms
    """

    _form_security_provider: FormSecurityProvider = None

    @classmethod
    def provide(cls, provider: FormSecurityProvider):
        """
        Set globally an instance of the form security provider
        :param provider: Form security implementation
        """
        cls._form_security_provider = provider

    @classmethod
    def inject(cls, ret_type: Union[Literal['input'], Literal['code']] = 'code') -> str:
        """
        Inject form security
        :param ret_type: Type of return for an input or only code
        :return: Injected code
        """
        if cls._form_security_provider is None:
            raise NotImplementedError()

        return cls._form_security_provider.do_inject(ret_type)

    @abstractmethod
    def do_inject(self, ret_type: Union[Literal['input'], Literal['code']]) -> str:
        """
        Inject form security
        :param ret_type: Type of return for an input or only code
        :return: Injected code
        """

        raise NotImplementedError()

    @classmethod
    def validate(cls, code: str) -> bool:
        """
        Validate de security code
        :param code: Retrieved code
        :return: Validation result
        """
        if cls._form_security_provider is None:
            raise NotImplementedError()

        return cls._form_security_provider.do_validate(code)

    @abstractmethod
    def do_validate(self, code: str) -> bool:
        """
        Validate de security code
        :param code: Retrieved code
        :return: Validation result
        """

        raise NotImplementedError()

    @classmethod
    def get_target_key(cls) -> str:
        """
        Get the target key on a expected request
        :return: Target key in a form
        """
        if cls._form_security_provider is None:
            raise NotImplementedError()

        return cls._form_security_provider.target_key

    @property
    @abstractmethod
    def target_key(self) -> str:
        raise NotImplementedError()