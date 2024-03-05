from __future__ import annotations
from typing import Optional, List
from infrastructure.utils.mysql import get_pool as get_mysql_pool, get_schema
from mysql.connector.pooling import PooledMySQLConnection
from mysql.connector.cursor import CursorBase
from domain.repositories import PostRepository, T
from domain.models import Post
from datetime import date
import domain.errors as err
from infrastructure.repositories import TableUnsafeEnsure, TableEnsure


class MysqlUnsafeRepository(PostRepository, TableUnsafeEnsure):
    TABLE_NAME = 'posts'

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
                    CREATE TABLE `posts` (
                        `ID` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
                        `TITLE` VARCHAR(150) NOT NULL,
                        `USER_NAME` VARCHAR(16) NOT NULL,
                        `CONTENT` TEXT NULL,
                        `CREATION_DATE` DATE NOT NULL DEFAULT CURRENT_TIMESTAMP
                    ); 
                ''')

                conn.commit()

    @TableUnsafeEnsure.ensure_table_exists
    def list(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Post]:
        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                cursor.execute('''
                    SELECT `TITLE`, `USER_NAME`, `CONTENT`, `ID`
                        FROM `{table!s}`
                    ORDER BY `CREATION_DATE` DESC, `ID` DESC
                '''.format(table=self.TABLE_NAME))

                data = cursor.fetchall()
                return [Post(title=row[0], user_name=row[1], content=row[2], _id=row[3]) for row in data]

    @TableUnsafeEnsure.ensure_table_exists
    def by_id(self, _id: int) -> Post:
        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                cursor.execute('''
                    SELECT `TITLE`, `USER_NAME`, `CONTENT`, `ID`, `CREATION_DATE`
                        FROM `{table!s}`
                    WHERE `ID` = {id:d}
                '''.format(table=self.TABLE_NAME, id=_id))

                data = cursor.fetchone()
                assert data is not None, err.NOT_FOUND.format(model='post', id=_id)
                return Post(title=data[0], user_name=data[1], content=data[2], _id=data[3], date=data[4])

    @TableUnsafeEnsure.ensure_table_exists
    def create(self, model: Post) -> int:
        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                cursor.execute('''
                INSERT INTO `{table!s}` (`TITLE`, `USER_NAME`, `CONTENT`)
                    VALUES ('{title!s}', '{user_name!s}', {content!s})
                '''.format(
                    table=self.TABLE_NAME,
                    title=model.title,
                    user_name=model.user_name,
                    content='NULL' if model.content is None else f"'{model.content!s}'",
                ))

                conn.commit()

                return cursor.lastrowid

    @TableUnsafeEnsure.ensure_table_exists
    def update(self, _id: int, model: Post):
        _ = self.by_id(_id)

        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                cursor.execute('''
                    UPDATE `{table!s}`
                        SET `TITLE` = '{title!s}', `CONTENT` = {content!s}
                        WHERE `ID` = {id:d}
                '''.format(
                    table=self.TABLE_NAME,
                    title=model.title,
                    content='NULL' if model.content is None else f"'{model.content!s}'",
                    id=_id,
                ))

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
                    raise AssertionError(err.NOT_FOUND.format(model='post', id=_id))

                conn.commit()

    @TableUnsafeEnsure.ensure_table_exists
    def filter(self, user_name: Optional[str] = None, title: Optional[str] = None) -> List[Post]:
        title = title or ''
        user_name = user_name or ''

        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                cursor.execute('''
                    SELECT `TITLE`, `USER_NAME`, `CONTENT`, `ID`
                        FROM `{table!s}`
                    WHERE `TITLE` LIKE '%{title!s}%' OR `USER_NAME` LIKE '%{user_name!s}%'
                    ORDER BY `CREATION_DATE` DESC, `ID` DESC
                '''.format(table=self.TABLE_NAME, title=title, user_name=user_name))

                data = cursor.fetchall()
                return [Post(title=row[0], user_name=row[1], content=row[2], _id=row[3]) for row in data]

    @TableUnsafeEnsure.ensure_table_exists
    def time_range(self, since: Optional[date] = None, until: Optional[date] = None) -> List[Post]:
        if since is None:
            since = date.min

        if until is None:
            until = date.max

        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor

                cursor.execute('''
                    SELECT `TITLE`, `USER_NAME`, `CONTENT`, `ID`
                        FROM `{table!s}`
                    WHERE `CREATION_DATE` BETWEEN '{since!s}' AND '{until!s}' 
                '''.format(table=self.TABLE_NAME, since=since, until=until))

                data = cursor.fetchall()
                return [Post(title=row[0], user_name=row[1], content=row[2], _id=row[3]) for row in data]


class MysqlRepository(PostRepository, TableEnsure):
    @TableEnsure.ensure_table_exists
    def list(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Post]:
        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor

                sql = '''
                    SELECT `TITLE`, `USER_NAME`, `CONTENT`, `ID`
                        FROM `posts`
                    ORDER BY `CREATION_DATE` DESC, `ID` DESC
                '''

                data = dict()

                if limit is not None:
                    sql += ' LIMIT %(limit)s OFFSET'
                    data['limit'] = limit
                    data['offset'] = offset or 0

                cursor.execute(sql, data)

                data = cursor.fetchall()
                return [Post(title=row[0], user_name=row[1], content=row[2], _id=row[3]) for row in data]

    @TableEnsure.ensure_table_exists
    def by_id(self, _id: int) -> Post:
        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                cursor.execute('''
                    SELECT `TITLE`, `USER_NAME`, `CONTENT`, `ID`, `CREATION_DATE`
                        FROM `posts`
                    WHERE `ID` = %(id)s
                ''', dict(id=_id))

                data = cursor.fetchone()
                assert data is not None, err.NOT_FOUND.format(model='post', id=_id)
                return Post(title=data[0], user_name=data[1], content=data[2], _id=data[3], date=data[4])

    @TableEnsure.ensure_table_exists
    def create(self, model: Post) -> int:
        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                cursor.execute('''
                INSERT INTO `posts` (`TITLE`, `USER_NAME`, `CONTENT`)
                    VALUES (%(title)s, %(user_name)s, %(content)s)
                ''', dict(
                    title=model.title,
                    user_name=model.user_name,
                    content=model.content,
                ))

                conn.commit()

                return cursor.lastrowid

    @TableEnsure.ensure_table_exists
    def update(self, _id: int, model: Post):
        _ = self.by_id(_id)

        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                cursor.execute('''
                    UPDATE `posts`
                        SET `TITLE` = %(title)s, `CONTENT` = %(content)s
                        WHERE `ID` = %(id)s
                ''', dict(
                    title=model.title,
                    content=model.content,
                    id=_id,
                ))

                conn.commit()

    @TableEnsure.ensure_table_exists
    def delete(self, _id: int):
        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                cursor.execute('''
                    DELETE FROM `posts`
                        WHERE `ID` = %(id)s''', dict(id=_id))

                if cursor.rowcount == 0:
                    conn.rollback()
                    raise AssertionError(err.NOT_FOUND.format(model='post', id=_id))

                conn.commit()

    @TableEnsure.ensure_table_exists
    def filter(self, user_name: Optional[str] = None, title: Optional[str] = None) -> List[Post]:
        title = f'%{title}%' if title is not None else '%%'
        user_name = f'%{user_name}%' if user_name is not None else '%%'

        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                cursor.execute('''
                    SELECT `TITLE`, `USER_NAME`, `CONTENT`, `ID`
                        FROM `posts`
                    WHERE `TITLE` LIKE %(title)s OR `USER_NAME` LIKE %(user_name)s
                    ORDER BY `CREATION_DATE` DESC, `ID` DESC
                ''', dict(title=title, user_name=user_name))

                data = cursor.fetchall()
                return [Post(title=row[0], user_name=row[1], content=row[2], _id=row[3]) for row in data]

    @TableEnsure.ensure_table_exists
    def time_range(self, since: Optional[date] = None, until: Optional[date] = None) -> List[Post]:
        if since is None:
            since = date.min

        if until is None:
            until = date.max

        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor

                cursor.execute('''
                    SELECT `TITLE`, `USER_NAME`, `CONTENT`, `ID`
                        FROM `posts`
                    WHERE `CREATION_DATE` BETWEEN %(since)s AND %(until)s 
                ''', dict(since=since, until=until))

                data = cursor.fetchall()
                return [Post(title=row[0], user_name=row[1], content=row[2], _id=row[3]) for row in data]

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
                ''', dict(schema=get_schema(), table='posts'))

                return cursor.fetchone()[0] > 0

    def create_table(self):
        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                cursor.execute('''
                    CREATE TABLE `posts` (
                        `ID` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
                        `TITLE` VARCHAR(150) NOT NULL,
                        `USER_NAME` VARCHAR(16) NOT NULL,
                        `CONTENT` TEXT NULL,
                        `CREATION_DATE` DATE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        
                        FOREIGN KEY (`USER_NAME`) REFERENCES `users` (`USER_NAME`)
                    ); 
                ''')

                conn.commit()
