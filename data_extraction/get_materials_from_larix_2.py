from icecream import ic
import psycopg2
from psycopg2.extras import DictRow
from pathlib import Path

from common_features import clean_text

#
from config import (
    PostgresDB,
    ais_access,
    DB_FILE,
    periods_pattern_name,
    # DUCK_DB_FILE
)

from sql_queries import sql_pg_queries
from data_extraction.materials_export import save_materials_support_db

def _get_period_id_title(database: PostgresDB, period_pattern: str) -> int | None:
    """Получить id периода  и название по регулярному выражению названия."""
    query = sql_pg_queries["select_larix_period_by_regexp_title"]
    period = database.select(query, {"regexp_pattern": period_pattern})
    return period[0]["id"], clean_text(period[0]["title"]) if period else None


def get_materials_from_larix(period_pattern: str) -> int | None:
    """Получить данные по материалам и историю цен из Larix для периода дополнения period_pattern.
    Получает историю цен для полученных материалов начиная с даты PRICE_HISTORY_START_DATE.
    Сохраняет все полученные данные в таблицу tblExpandedMaterial SQLite БД."""
    table = None

    with PostgresDB(ais_access) as db:
        larix_period = _get_period_id_title(db, period_pattern)
        if larix_period:
            larix_period_id, larix_period_title = larix_period
            ic(larix_period)
        else:
            return None
        query = sql_pg_queries["select_materials_for_period_id"]
        materials = db.select(query, {"period_id": larix_period_id})
        if materials:
            ic("прочитано материалов: ", len(materials))
            save_materials_support_db(DB_FILE, larix_period_id, materials)
    return 0 if materials else None



if __name__ == "__main__":
    ic()
    get_materials_from_larix(periods_pattern_name["supplement_72"])
