
import psycopg2
from psycopg2.extras import DictCursor
from contextlib import closing
import traceback
from typing import Optional, Type
from types import TracebackType

from config.pg_connect import DatabaseAccess


class PostgresDB:
    """PostgreSQL class."""
    def __init__(self, db_access: DatabaseAccess):
        self.db_access = db_access
        self.connection = None
        self.cursor = None
        self.default_limit = 10

    def connect(self):
        """Connect to the database."""
        if self.connection is None:
            try:
                self.connection = psycopg2.connect(**self.db_access.as_dict())
            except psycopg2.DatabaseError as e:
                raise e



    def __enter__(self):
        self.connect()
        if self.connection:
            self.cursor = self.connection.cursor(cursor_factory=DictCursor)
            return self
        return None

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType],
        ):
        if exc_val:
            traceback.print_exc()
            print(f'произошла непредвиденная ошибка при закрытии БД {self.db_access.database}')
            raise exc_val
        if self.cursor:
            try:
                self.cursor.close()
            except psycopg2.DatabaseError as e:
                traceback.print_exc(e)
                raise e
        if self.connection:
            try:
                self.connection.close()
            except psycopg2.DatabaseError as e:
                traceback.print_exc(e)
                raise e
        self.cursor, self.connect = None, None


    def update_rows(self, query) -> str | None:
        """ update rows """
        self.connect()
        if self.connection:
            with closing(self.connection) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    return f"{cursor.rowcount} строк обновлено."
        return None


    def select_rows_dict_cursor(self, query, args=None):
        """ SELECT as dicts."""
        self.connect()
        with closing(self.connection) as conn:
        # with self.connection as conn:
            try:
                self.cursor.execute(query, args)
                records = self.cursor.fetchall()
            except psycopg2.DatabaseError as e:
                print(e)
                raise e
        return records if records else None



if __name__ == "__main__":
    from sql_queries.sql_pg_export import sql_export
    from pg_connect import ais_access
    from pprint import pprint


    with PostgresDB(ais_access) as db:
        query = sql_export["test_sql"]
        query_parameter = {"period_ids": (150862302, 150996873)}

        result = db.select_rows_dict_cursor(query, query_parameter)
        print("\n", len(result))

        pprint([dict(x) for x in result])

        # with db.connection.cursor() as cur:
        #     with open( "test.csv", "w", encoding="utf-8") as file:
        #         cur.copy_from(file, "tblRawData", sep=",")