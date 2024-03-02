from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List, Tuple
from domain.models import User, Post
from datetime import date

T = TypeVar('T')


class Repository(Generic[T], ABC):
    """
    Generic repository accessor interface
    """

    @abstractmethod
    def list(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[T]:
        raise NotImplementedError()

    @abstractmethod
    def by_id(self, _id: int) -> T:
        raise NotImplementedError()

    @abstractmethod
    def create(self, model: T) -> int:
        raise NotImplementedError()

    @abstractmethod
    def update(self, _id: int, model: T):
        raise NotImplementedError()

    @abstractmethod
    def delete(self, _id: int):
        raise NotImplementedError()


class UserRepository(Repository[User], ABC):
    @abstractmethod
    def by_login(self, user_name: str, password: str) -> Tuple[User, int]:
        raise NotImplementedError()

    @abstractmethod
    def by_user_id(self, user_name: str) -> User:
        raise NotImplementedError()


class PostRepository(Repository[Post], ABC):
    @abstractmethod
    def filter(self, user_name: Optional[str] = None, title: Optional[str] = None) -> List[Post]:
        raise NotImplementedError()

    @abstractmethod
    def time_range(self, since: Optional[date] = None, until: Optional[date] = None) -> List[Post]:
        raise NotImplementedError()
