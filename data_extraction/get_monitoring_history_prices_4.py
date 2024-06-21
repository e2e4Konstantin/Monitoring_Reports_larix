import sqlite3
from icecream import ic

from DB_support.sql_sqlite_monitoring import sql_sqlite_monitoring
from DB_support.db_config import SQLiteDB

from psycopg2.extras import DictRow as pg_DictRow
from config import (
    PostgresDB,
    ais_access,
    PRICE_HISTORY_START_DATE,
    DB_FILE
    )
from sql_queries import sql_pg_queries
from common_features import code_to_number


def _get_monitoring_history_prices_(db: PostgresDB, start_date: str) -> list[pg_DictRow] | None:
    """Получает минимальные цены для периодов для данных мониторинга, начиная с заданной даты."""
    monitoring_prices = db.select(
        sql_pg_queries["select_monitoring_min_prices_for_periods_starting_date"],
        {"start_date": start_date},
    )
    return monitoring_prices

def _prepare_monitoring_history_price_data(price: pg_DictRow)->tuple:
    """Преобразует данные из pg_DictRow в кортеж для SQLiteDB."""
    # code, digit_code, period_name, index_number, period_title, resource_id,
    # transport_included_in_price, price, min_price, agent_name
    result = (
        price["code"],
        code_to_number(price["code"]),
        price["period_name"],
        price["index_number"],
        price["period_title"],
        price["resource_id"],
        price["transport_included_in_price"],
        price["price"],
        price["min_price"],
        price["agent_name"],
    )
    return result


def _save_monitoring_prices_sqlite_db(
    db_file: str, list_of_prices: list[pg_DictRow] = None
):
    """
    Сохранить историю цен мониторинга в  в SQLite db_file.
    """
    with SQLiteDB(db_file) as db:
        db.go_execute(sql_sqlite_monitoring["delete_table_monitoring_history_prices"])
        db.go_execute(sql_sqlite_monitoring["create_table_monitoring_history_prices"])
        db.go_execute(sql_sqlite_monitoring["create_index_monitoring_history_prices"])
        #
        for price in list_of_prices:
            data = _prepare_monitoring_history_price_data(price)
            db.go_execute(
                sql_sqlite_monitoring["insert_row_monitoring_history_prices"],
                data,
            )


def _create_pivot_monitoring_index(db_file: str):
    """Создает разворотную таблицу tblPivotMonitoringIndex с ценами по шифру и
    с номерами индексных периодов в названиях столбцов."""
    ic()
    with SQLiteDB(db_file) as db:
        codes = db.go_select(
            sql_sqlite_monitoring["select_unique_code_monitoring_history_price"]
        )
        codes = tuple([x["code"] for x in codes])
        ic("всего шифров: ", len(codes))
        indexes = db.go_select(
            sql_sqlite_monitoring["select_unique_index_number_monitoring_history_price"]
        )
        if indexes is None:
            return None
        ic("всего периодов: ", len(indexes))
        ic("первый индексный период: ", tuple(indexes[0]))
        columns = [str(x["index_number"]) for x in indexes]
        # ic(columns)

        db.go_execute(sql_sqlite_monitoring["delete_table_pivot_monitoring_index"])
        db.go_execute(sql_sqlite_monitoring["create_table_pivot_monitoring_index"])
        for column in columns:
            query = f'ALTER TABLE tblPivotMonitoringIndex ADD COLUMN "{column}" REAL;'
            db.go_execute(query)

        for code in codes:
            result = db.go_select(
                sql_sqlite_monitoring["select_code_monitoring_history_price"],
                (code,),
            )
            digit_code = result[0]["digit_code"]
            # ic(code, digit_code)
            code_data = {x["index_number"]: x["price"] for x in result}
            # ic(code_data)
            insert_values = [code_data.get(int(x), None) for x in columns]
            # ic(insert_values)
            insert_data = code, digit_code, *insert_values
            # ic(insert_data)

            query_head = (
                r"INSERT INTO tblPivotMonitoringIndex (code, digit_code, "
                + ", ".join([f'"{x}"' for x in columns])
            )
            query_tail = (
                ") VALUES ( ?, ?, "
                + ", ".join(["?" for x in range(len(columns))])
                + ");"
            )

            query = query_head + query_tail
            # ic(query)
            db.go_execute(query, insert_data)




def get_monitoring_materials_from_larix(sqlite_db_file: str, start_date: str):
    """
    Получить данные по мониторингу из larix.
    Запомнить прочитанные данные в таблицу tblMonitoringMaterials SQLite.
    Глубина истории цен берется только для индексных периодов начиная с даты start_date.
    Создает разворотную таблицу tblPivotMonitoringIndex с номерами периодов в столбцах.
    """
    monitoring_prices = None
    with PostgresDB(ais_access) as db:
        monitoring_prices = _get_monitoring_history_prices_(db, start_date)
        ic(len(monitoring_prices))
    if monitoring_prices:
        _save_monitoring_prices_sqlite_db(sqlite_db_file, monitoring_prices)
        _create_pivot_monitoring_index(sqlite_db_file)


if __name__ == "__main__":
    ic()
    get_monitoring_materials_from_larix(DB_FILE, PRICE_HISTORY_START_DATE)