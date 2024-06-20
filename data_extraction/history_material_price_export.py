import sqlite3
from icecream import ic

from DB_support.sql_sqlite_materials import sql_sqlite_materials
from DB_support.sql_sqlite_periods import sql_sqlite_periods
from DB_support.db_config import SQLiteDB
from psycopg2.extras import DictRow as pg_DictRow
from common_features import code_to_number, output_message_exit


def _get_sqlite_period_by_larix_period_id(db: SQLiteDB, larix_period_id: int) -> sqlite3.Row | None:
    """Возвращает данные о периоде по larix_period_id."""
    result = db.go_select(
        sql_sqlite_periods["select_by_larix_id"],
        {"larix_period_id": larix_period_id},
    )
    return result[0] if result else None


def _prepare_history_price_material_data(db: SQLiteDB, price: pg_DictRow) -> tuple:
    """Преобразует данные из pg_DictRow в кортеж для SQLiteDB."""
    larix_period_id = price["larix_period_id"]
    period = _get_sqlite_period_by_larix_period_id(db, larix_period_id)
    if not period:
        output_message_exit(
            "В таблице 'tblPeriods'", f"Не найден период: {larix_period_id=}"
        )
    data = {
        "code": price["code"],
        "base_price": price["base_price"],
        "current_price": price["current_price"],
        "index_number": price["index_number"],
        "net_weight": price["net_weight"],
        "gross_weight": price["gross_weight"],
        "transport_code": price["transport_code"],
        "transport_name": price["transport_name"],
        "transport_base_price": price["transport_base_price"],
        "transport_current_price": price["transport_current_price"],
        "storage_cost_rate": price["storage_rate"],
        "storage_cost_name": price["storage_name"],
        "storage_cost_description": price["storage_description"],
        #
        "period_id": period["id"],
        "digit_code": code_to_number(price["code"]),
    }
    return data


def save_materials_history_prices_sqlite_db(
    db_file: str, list_of_prices: list[pg_DictRow] = None
):
    """
    Сохранить историю цен на материалы в  в SQLite db_file.
    """
    with SQLiteDB(db_file) as db:
        db.go_execute(sql_sqlite_materials["delete_table_history_price_materials"])
        db.go_execute(sql_sqlite_materials["create_table_history_price_materials"])
        db.go_execute(sql_sqlite_materials["create_index_history_price_materials"])
        #
        for price in list_of_prices:
            data = _prepare_history_price_material_data(db, price)
            db.go_execute(
                sql_sqlite_materials["insert_row_history_price_materials"], data
            )

def create_materials_pivot_table_by_index_number(db_file: str):
    """
    Создает таблицу tblPivotIndex в SQLite db_file. Разворачивает таблицу tblHistoryPriceMaterials по индексным периодам.
    """
    with SQLiteDB(db_file) as db:
        codes = db.go_select(
            sql_sqlite_materials["select_unique_code_history_price_materials"]
        )
        codes = tuple([x["code"] for x in codes])
        ic("в tblHistoryPriceMaterials уникальных шифров: ", len(codes))
        indexes = db.go_select(
            sql_sqlite_materials["select_unique_index_number_history_price_materials"]
        )
        if indexes is None:
            return None
        ic("первый индексный период: ", tuple(indexes[0]))
        columns = [str(x["index_number"]) for x in indexes]
        # ic(columns)

        db.go_execute(sql_sqlite_materials["delete_table_pivot_index_materials"])
        db.go_execute(sql_sqlite_materials["create_table_pivot_index_materials"])
        for column in columns:
            # query = f'ALTER TABLE tblPivotIndexMaterials ADD COLUMN "{column}" REAL;'
            # db.go_execute(query)
            query = sql_sqlite_materials["insert_column_to_pivot_index_materials"].format(column)
            db.go_execute(query)

        for code in codes:
            result = db.go_select(
                sql_sqlite_materials["select_code_history_price_materials"], (code,)
            )
            digit_code = result[0]["digit_code"]
            # ic(code, digit_code)
            code_data ={x["index_number"]: x["current_price"]
                         for x in result
            }
            # ic(code_data)
            insert_values = [
                code_data.get(int(x), None) for x in columns
            ]
            # ic(insert_values)
            insert_data = code, digit_code, *insert_values
            # ic(insert_data)

            query_head = (
                r"INSERT INTO tblPivotIndexMaterials (code, digit_code, "
                + ", ".join([f'"{x}"' for x in columns])
            )
            query_tail = ") VALUES ( ?, ?, " + ", ".join(["?" for x in range(len(columns))]) + ");"

            query = query_head + query_tail
            # ic(query)
            db.go_execute(query, insert_data)

