from abc import ABC, abstractmethod
from typing import Callable
from functools import wraps


class TableUnsafeEnsure(ABC):
    """
    Utility to ensure and create a table in a repositories
    """

    TABLE_NAME = '<not implemented>'

    @property
    @abstractmethod
    def table_exists(self) -> bool:
        """
        Ensure if the table exists
        :return: Validity
        """
        raise NotImplementedError()

    @abstractmethod
    def create_table(self):
        """
        Create the table
        """
        raise NotImplementedError()

    @staticmethod
    def ensure_table_exists(fx: Callable):
        """
        Decorator to ensure and create table if it does not exist
        :param fx: Function to wraps
        :return: Wrapped function
        """
        @wraps(fx)
        def wrapper(self: TableUnsafeEnsure, *args, **kwargs):
            if not self.table_exists:
                self.create_table()
            return fx(self, *args, **kwargs)

        return wrapper
