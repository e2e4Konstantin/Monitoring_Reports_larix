from DB_support.sql_sqlite_materials import sql_sqlite_materials
from DB_support.db_config import SQLiteDB
from psycopg2.extras import DictRow as pg_DictRow





def save_history_prices_support_db(
    db_file: str, list_of_prices: list[pg_DictRow] = None
):
    """
    Сохранить список цен на материалы в  в SQLite db_file.
    """
    with SQLiteDB(db_file) as db:
        db.go_execute(sql_sqlite_materials["delete_table_history_price_materials"])
        db.go_execute(sql_sqlite_materials["create_table_history_price_materials"])
        db.go_execute(sql_sqlite_materials["create_index_history_price_materials"])
        #
        for price in list_of_prices:
            data = _prepare_material_data(material, period)
            db.go_execute(sql_sqlite_materials["insert_row_expanded_material"], data)
