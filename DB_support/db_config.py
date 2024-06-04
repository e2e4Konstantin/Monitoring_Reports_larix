import sqlite3
import re
from icecream import ic
from config import DB_FILE

from common_features import output_message_exit, output_message


class SQLiteController:
    """Класс для управления подключением к базе данных."""
    def __init__(self, db_file_name: str):
        self.db_file_name = db_file_name
        self.connection = self.connect()

    @staticmethod
    def regex_search(pattern, text):
        """
        Поиск шаблона в заданном тексте с помощью регулярных выражений.
        """
        return bool(re.search(pattern, text))

    @staticmethod
    def clean_non_utf8_chars(input_string: str) -> str:
        """
        Удаление из строки символов, не относящихся к стандартуUTF8
        """
        return input_string.encode("utf-8").decode("utf-8", "ignore")

    def connect(self):
        try:
            connection = sqlite3.connect(self.db_file_name)
            connection.row_factory = sqlite3.Row
            connection.create_function("regexp", 2, self.regex_search)
            # включить проверку целостности таблиц
            # self.connection.execute("PRAGMA foreign_keys = ON;")
            return connection
        except sqlite3.Error as error:
            raise ConnectionError(f"Error opening SQLite database: {error}")


    def close(self, exception=None):
        if self.connection:
            if exception is not None:
                self.connection.rollback()
            else:
                self.connection.commit()
            self.connection.close()
            self.connection = None


class SQLiteDB(SQLiteController):
    """Класс для работы с базой данных."""

    def __init__(self, db_file_name: str):
        super().__init__(db_file_name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __str__(self):
        return f"Database name: {self.db_file_name}, connection: {self.connection}"

    def __del__(self):
        self.close()


    def go_insert(self, query: str, src_data: tuple, message: str) -> int | None:
        """ Пытается выполнить запрос на вставку записи в БД. Возвращает rowid """
        try:
            result = self.connection.execute(query, src_data)
            if result:
                return result.lastrowid
            output_message(
                f"ошибка INSERT запроса к БД Sqlite3: {src_data}", f"{message}",
            )
            return None
        except sqlite3.Error as error:
            output_message(
                f"ошибка INSERT запроса к БД Sqlite3: {' '.join(error.args)}",
                f"{message}",
            )

    def go_select(self, query: str, src_data: tuple = None) -> list[sqlite3.Row] | None:
        """ Пытается выполнить запрос на выборку записей из БД. Возвращает список строк. """
        try:
            if src_data:
                cursor = self.connection.execute(query, src_data)
            else:
                cursor = self.connection.execute(query)
            return cursor.fetchall() if cursor else None
        except sqlite3.Error as error:
            output_message_exit(f"ошибка SELECT запроса БД Sqlite3: {' '.join(error.args)}", f"{src_data}")
        return None


    def go_execute(self, query, *args) -> sqlite3.Cursor | None:
        ''' Execute SQL '''
        try:
            result = self.connection.execute(query, *args)
            return result
        except sqlite3.Error as error:
            output_message(f"ошибка запроса БД Sqlite3: {' '.join(error.args)}", f"{args}\n{query} ")

    def go_execute_many(self, query, *args) -> sqlite3.Cursor | None:
        """Execute SQL"""
        try:
            result = self.connection.executemany(query, *args)
            return result
        except sqlite3.Error as error:
            output_message(
                f"ошибка запроса БД Sqlite3: {' '.join(error.args)}",
                f"{args}\n{query} ",
            )


    def inform(self, all_details: bool = False):
        """  Выводи в консоль информацию о таблицах БД
        :param all_details: выводить все записи
        """
        if self.connection:
            with self.connection as db:
                cursor = self.connection.execute('SELECT SQLITE_VERSION()')
                print(f"SQLite version: {cursor.fetchone()[0]}")
                print(f"connect.total_changes: {db.total_changes}")

                cursor = self.connection.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                for index, table_i in enumerate(tables):
                    table_name = table_i[0]
                    count = self.connection.execute(f"SELECT COUNT(1) from {table_name}")
                    print(f"\n{index + 1}. таблица: {table_name}, записей: {count.fetchone()[0]}")
                    table_info = self.connection.execute(f"PRAGMA table_info({table_name})")
                    data = table_info.fetchall()

                    print("поля таблицы: ")
                    print([tuple(d) for d in data])
                    if all_details:
                        print("данные таблицы:")
                        cursor = self.connection.execute(f"SELECT * from {table_name}")
                        print([row_i for row_i in cursor])


if __name__ == '__main__':

    s = "Hello, world! 😀"
    db_name = DB_FILE
    ic(db_name)

    db = SQLiteDB(db_name)
    [result] = db.go_select("SELECT COUNT(*) AS 'Count' FROM tblDirectories;")
    ic(result['Count'])
    db.inform()
    db.close()
    #
    with SQLiteDB(db_name) as db:
        [result] = db.go_execute("SELECT rowid as rowid, * FROM tblDirectories WHERE name = 'test';" )
        ic(result.keys())
        ic(result['rowid'])
