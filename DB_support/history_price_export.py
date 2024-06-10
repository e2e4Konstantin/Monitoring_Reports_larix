import sqlite3
from icecream import ic

from DB_support.sql_sqlite_materials import sql_sqlite_materials
from DB_support.db_config import SQLiteDB
from psycopg2.extras import DictRow as pg_DictRow
from common_features import code_to_number


def _prepare_history_price_material_data(price: sqlite3.Row) -> tuple:
    result = (
        price["code"],
        code_to_number(price["code"]),
        price["base_price"],
        price["current_price"],
        price["index_number"],
    )
    return result




def save_history_prices_sqlite_db(
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
            data = _prepare_history_price_material_data(price)
            db.go_execute(
                sql_sqlite_materials["insert_row_history_price_materials"], data
            )

def create_pivot_table_by_index_number(db_file: str):
    """

    """
    with SQLiteDB(db_file) as db:
        codes = db.go_select(
            sql_sqlite_materials["select_unique_code_history_price_materials"]
        )
        print(len(codes))
        indexes = db.go_select(
            sql_sqlite_materials["select_unique_index_number_history_price_materials"]
        )
        if indexes is None:
            return None
        ic(tuple(indexes[0]))
        columns = [str(x["index_number"]) for x in indexes]
        ic(columns)

        db.go_execute(sql_sqlite_materials["delete_table_pivot_index_number"])
        db.go_execute(sql_sqlite_materials["create_table_pivot_index_number"])
        for column in columns:
            query = f'ALTER TABLE tblPivotIndex ADD COLUMN "{column}" REAL;'
            db.go_execute(query)


        for code in codes:
            result = db.go_select(
                sql_sqlite_materials["select_code_history_price_materials"], code
            )
            code_data = [(x["index_number"], x["base_price"], x["current_price"])
                         for x in result
                         ]
            ic(code_data)

            dd = [x[2] for x in code_data]
            dd.insert(0, code[0])
            print(dd)
            # query_insert = f"INSERT INTO tblHistoryPriceMaterials (code, digit_code, base_price, current_price, index_number) VALUES ( ?, ?, ?, ?, ? );"
            query_head = r"INSERT INTO tblPivotIndex (code, " + ", ".join(
                [f'"{x}"' for x in columns]
            )

            query_tail = ") VALUES ( ?, " + ", ".join(["?" for x in range(len(columns))]) + ");"

            query = query_head + query_tail
            ic(query)
            db.go_execute(query, dd)

