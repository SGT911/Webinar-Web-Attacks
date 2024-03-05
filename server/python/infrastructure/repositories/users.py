from __future__ import annotations
from typing import Optional, List, Tuple
from infrastructure.utils.mysql import get_pool as get_mysql_pool, get_schema
from mysql.connector.pooling import PooledMySQLConnection
from mysql.connector.cursor import CursorBase
from domain.repositories import UserRepository
from domain.models import User
import domain.errors as err
from infrastructure.repositories import TableUnsafeEnsure, TableEnsure


class MysqlUnsafeRepository(UserRepository, TableUnsafeEnsure):
    TABLE_NAME = 'users'

    @property
    def __connection(self) -> PooledMySQLConnection:
        return get_mysql_pool().get_connection()

    @property
    def table_exists(self) -> bool:
        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                cursor.execute('''
                    SELECT
                        COUNT(*)
                    FROM `information_schema`.`TABLES`
                        WHERE `TABLE_SCHEMA` = '{schema!s}'
                          AND `TABLE_NAME` = '{table!s}'
                '''.format(schema=get_schema(), table=self.TABLE_NAME))

                return cursor.fetchone()[0] > 0

    def create_table(self):
        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                cursor.execute('''
                    CREATE TABLE `users` (
                        `ID` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
                        `USER_NAME` VARCHAR(16) NOT NULL,
                        `FULL_NAME` VARCHAR(255) NOT NULL,
                        `PASSWORD` BLOB NULL
                    ); 
                ''')

                conn.commit()

    @TableUnsafeEnsure.ensure_table_exists
    def by_login(self, user_name: str, password: str) -> Tuple[User, int]:
        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                cursor.execute('''
                    SELECT `USER_NAME`, `FULL_NAME`, `PASSWORD`, `ID`
                        FROM `{table!s}`
                    WHERE `USER_NAME` = '{user_name!s}'
                '''.format(table=self.TABLE_NAME, user_name=user_name))

                data = cursor.fetchone()
                if data is None:
                    raise AssertionError(err.INVALID_CREDENTIAL)

                user = User(user_name=data[0], full_name=data[1], password=data[2])
                assert user.verify_password(password), err.INVALID_CREDENTIAL

                return user, data[3]

    @TableUnsafeEnsure.ensure_table_exists
    def list(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[User]:
        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                cursor.execute('''
                    SELECT `USER_NAME`, `FULL_NAME`
                        FROM `{table!s}`
                '''.format(table=self.TABLE_NAME))

                data = cursor.fetchall()
                return [User(user_name=row[0], full_name=row[1]) for row in data]

    @TableUnsafeEnsure.ensure_table_exists
    def by_id(self, _id: int) -> User:
        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                cursor.execute('''
                    SELECT `USER_NAME`, `FULL_NAME`
                        FROM `{table!s}`
                    WHERE `ID` = {id:d}
                '''.format(table=self.TABLE_NAME, id=_id))

                data = cursor.fetchone()
                assert data is not None, err.NOT_FOUND.format(model='user', id=_id)
                return User(user_name=data[0], full_name=data[1])

    @TableUnsafeEnsure.ensure_table_exists
    def create(self, model: User) -> int:
        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                cursor.execute('''
                INSERT INTO `{table!s}` (`USER_NAME`, `FULL_NAME`, `PASSWORD`)
                    VALUES ('{user_name!s}', '{full_name!s}', CONVERT('{password!s}' USING BINARY))
                '''.format(
                    table=self.TABLE_NAME,
                    user_name=model.user_name,
                    full_name=model.full_name,
                    password=model.password.decode(),
                ))

                conn.commit()

                return cursor.lastrowid

    @TableUnsafeEnsure.ensure_table_exists
    def update(self, _id: int, model: User):
        _ = self.by_id(_id)

        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                cursor.execute('''
                    UPDATE `{table!s}`
                        SET `USER_NAME` = '{user_name!s}', `FULL_NAME` = '{full_name!s}'
                        WHERE `ID` = {id:d}
                '''.format(table=self.TABLE_NAME, user_name=model.user_name, full_name=model.full_name, id=_id))

                if hasattr(model, 'password') and model.password is not None:
                    cursor.execute('''
                        UPDATE `{table!s}`
                            SET `PASSWORD` = CONVERT('{password!s}' USING BINARY)
                            WHERE `ID` = {id:d}
                    '''.format(table=self.TABLE_NAME, password=model.password.decode(), id=_id))

                conn.commit()

    @TableUnsafeEnsure.ensure_table_exists
    def delete(self, _id: int):
        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                cursor.execute('''
                    DELETE FROM `{table!s}`
                        WHERE `ID` = {id:d}'''.format(table=self.TABLE_NAME, id=_id))

                if cursor.rowcount == 0:
                    conn.rollback()
                    raise AssertionError(err.NOT_FOUND.format(model='user', id=_id))

                conn.commit()

    @TableUnsafeEnsure.ensure_table_exists
    def by_user_id(self, user_name: str) -> User:
        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                cursor.execute('''
                    SELECT `USER_NAME`, `FULL_NAME`
                        FROM `{table!s}`
                    WHERE `USER_NAME` = '{user_name!s}'
                '''.format(table=self.TABLE_NAME, user_name=user_name))

                data = cursor.fetchone()
                assert data is not None, err.NOT_FOUND.format(model='user', id=user_name)
                return User(user_name=data[0], full_name=data[1])


class MysqlRepository(UserRepository, TableEnsure):
    @TableEnsure.ensure_table_exists
    def by_login(self, user_name: str, password: str) -> Tuple[User, int]:
        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                cursor.execute('''
                    SELECT `USER_NAME`, `FULL_NAME`, `PASSWORD`, `ID`
                        FROM `users`
                    WHERE `USER_NAME` = %(user_name)s
                        LIMIT 1
                ''', dict(user_name=user_name))

                data = cursor.fetchone()
                user = User(user_name=data[0], full_name=data[1], password=data[2])
                assert user.verify_password(password), err.INVALID_CREDENTIAL

                return user, data[3]

    @TableEnsure.ensure_table_exists
    def by_user_id(self, user_name: str) -> User:
        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                cursor.execute('''
                    SELECT `USER_NAME`, `FULL_NAME`
                        FROM `users`
                    WHERE `USER_NAME` = %(user_name)s
                        LIMIT 1
                ''', dict(user_name=user_name))

                data = cursor.fetchone()
                assert data is not None, err.NOT_FOUND.format(model='user', id=user_name)
                return User(user_name=data[0], full_name=data[1])

    @TableEnsure.ensure_table_exists
    def list(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[User]:
        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                sql = '''
                    SELECT `USER_NAME`, `FULL_NAME`
                        FROM `users`
                '''

                data = dict()

                if limit is not None:
                    sql += ' LIMIT %(limit)s OFFSET'
                    data['limit'] = limit
                    data['offset'] = offset or 0

                cursor.execute(sql, data)
                data = cursor.fetchall()
                return [User(user_name=row[0], full_name=row[1]) for row in data]

    @TableEnsure.ensure_table_exists
    def by_id(self, _id: int) -> User:
        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                cursor.execute('''
                    SELECT `USER_NAME`, `FULL_NAME`
                        FROM `users`
                    WHERE `ID` = %(id)s
                        LIMIT 1
                ''', dict(id=_id))

                data = cursor.fetchone()
                assert data is not None, err.NOT_FOUND.format(model='user', id=_id)
                return User(user_name=data[0], full_name=data[1])

    @TableEnsure.ensure_table_exists
    def create(self, model: User) -> int:
        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                cursor.execute('''
                INSERT INTO `users` (`USER_NAME`, `FULL_NAME`, `PASSWORD`)
                    VALUES (%(user_name)s, %(full_name)s, %(password)s)
                ''', dict(
                    user_name=model.user_name,
                    full_name=model.full_name,
                    password=model.password,
                ))

                conn.commit()

                return cursor.lastrowid

    @TableEnsure.ensure_table_exists
    def update(self, _id: int, model: User):
        _ = self.by_id(_id)

        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                cursor.execute('''
                    UPDATE `users`
                        SET `USER_NAME` = %(user_name)s, `FULL_NAME` = %(user_name)s
                        WHERE `ID` = %(id)s LIMIT 1
                ''', dict(user_name=model.user_name, full_name=model.full_name, id=_id))

                if hasattr(model, 'password') and model.password is not None:
                    cursor.execute('''
                        UPDATE `users`
                            SET `PASSWORD` = %(password)s
                            WHERE `ID` = %(id)s LIMIT 1
                    ''', dict(password=model.password.decode(), id=_id))

                conn.commit()

    @TableEnsure.ensure_table_exists
    def delete(self, _id: int):
        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                cursor.execute('''
                    DELETE FROM `users`
                        WHERE `ID` = %(id)s LIMIT 1''', dict(id=_id))

                if cursor.rowcount == 0:
                    conn.rollback()
                    raise AssertionError(err.NOT_FOUND.format(model='user', id=_id))

                conn.commit()

    @property
    def __connection(self) -> PooledMySQLConnection:
        return get_mysql_pool().get_connection()

    @property
    def table_exists(self) -> bool:
        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                cursor.execute('''
                    SELECT
                        COUNT(*)
                    FROM `information_schema`.`TABLES`
                        WHERE `TABLE_SCHEMA` = %(schema)s
                          AND `TABLE_NAME` = %(table)s
                ''', dict(schema=get_schema(), table='users'))

                return cursor.fetchone()[0] > 0

    def create_table(self):
        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                cursor.execute('''
                    CREATE TABLE `users` (
                        `ID` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
                        `USER_NAME` VARCHAR(16) NOT NULL UNIQUE,
                        `FULL_NAME` VARCHAR(255) NOT NULL,
                        `PASSWORD` BLOB NULL
                    ); 
                ''')

                conn.commit()
