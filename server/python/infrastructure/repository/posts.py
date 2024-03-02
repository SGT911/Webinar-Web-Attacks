from __future__ import annotations
from typing import Optional, List, Tuple
from infrastructure.utils.mysql import get_pool as get_mysql_pool, get_schema
from mysql.connector.pooling import PooledMySQLConnection
from mysql.connector.cursor import CursorBase
from domain.repository import PostRepository
from domain.models import Post
import domain.errors as err
from infrastructure.repository import TableUnsafeEnsure


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
                        `CONTENT` TEXT NULL
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
                '''.format(table=self.TABLE_NAME))

                data = cursor.fetchall()
                return [Post(title=row[0], user_name=row[1], content=row[2], _id=row[3]) for row in data]

    @TableUnsafeEnsure.ensure_table_exists
    def by_id(self, _id: int) -> Post:
        with self.__connection as conn:
            with conn.cursor() as cursor:
                cursor: CursorBase = cursor
                cursor.execute('''
                    SELECT `TITLE`, `USER_NAME`, `CONTENT`, `ID`
                        FROM `{table!s}`
                    WHERE `ID` = {id:d}
                '''.format(table=self.TABLE_NAME, id=_id))

                data = cursor.fetchone()
                assert data is not None, err.NOT_FOUND.format(model='post', id=_id)
                return Post(title=data[0], user_name=data[1], content=data[2], _id=data[3])

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
                    WHERE `TITLE` LIKE '%{title!s}%' AND `USER_NAME` LIKE '%{user_name!s}%'
                '''.format(table=self.TABLE_NAME, title=title, user_name=user_name))

                data = cursor.fetchall()
                return [Post(title=row[0], user_name=row[1], content=row[2], _id=row[3]) for row in data]
