from icecream import ic
import psycopg2
from psycopg2.extras import DictRow
from pathlib import Path

from common_features import clean_text

#
from config import (
    PostgresDB,
    ais_access,
    PRICE_HISTORY_START_DATE,
    DB_FILE,
    # DUCK_DB_FILE
)

from sql_queries import sql_pg_queries

from data_extraction.history_material_price_export import (
    save_materials_history_prices_sqlite_db,
    create_materials_pivot_table_by_index_number
)


def _get_price_history_for_all_materials(
    db: PostgresDB, start_date: str
) -> list[DictRow] | None:
    """Получение истории цен на материалы, начиная с заданной даты."""
    prices = db.select(
        sql_pg_queries["select_prices_all_materials_for_target_periods"],
        {"start_date": start_date},
    )
    return prices if prices else None


def get_history_prices_materials_from_larix(history_start_date: str) -> int | None:
    """
    Получает историю цен материалов начиная с даты PRICE_HISTORY_START_DATE.
    Сохраняет данные tblHistoryPriceMaterials в SQLite БД.
    Строит развернутую по периодам таблицу с историей цен материалов.
    Сохраняет в tblPivotIndexMaterials.
    """

    with PostgresDB(ais_access) as db:
        prices = _get_price_history_for_all_materials(db, history_start_date)
        ic("история цен материалов: ", len(prices))
    if not prices:
        return None
    save_materials_history_prices_sqlite_db(DB_FILE, prices)
    create_materials_pivot_table_by_index_number(DB_FILE)
    #
    # for DuckDB
    # save_history_prices_support_duck_db(DUCK_DB_FILE, prices)
    # show_pivot_table_duck_db(DUCK_DB_FILE)
    return 0 if prices else None


if __name__ == "__main__":
    ic()
    get_history_prices_materials_from_larix(PRICE_HISTORY_START_DATE)

