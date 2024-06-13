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
    periods_pattern_name,
    DUCK_DB_FILE
)
from models import Material, ProductType, HistoricPrice, MiniPeriod
from sql_queries import sql_pg_queries

from data_extraction.history_material_price_export import (
    save_materials_history_prices_sqlite_db,
    create_materials_pivot_table_by_index_number,
)



# from data_extraction.history_material_price_export import (
#     save_materials_history_prices_sqlite_db,
#     create_pivot_table_by_index_number,
# )

from data_extraction.materials_export import save_materials_support_db



def _get_price_history_for_all_materials(
    db: PostgresDB, start_date: str
) -> list[DictRow] | None:
    """Получение истории цен на все материалы, начиная с заданной даты."""
    prices = db.select(
        sql_pg_queries["select_prices_all_materials_for_target_periods"],
        {"start_date": start_date},
    )
    # ic(dict(prices[0]).keys())
    # for price in prices:
    #     print(price)
    #     price["base_price"] = float(price["base_price"])
    #     price["current_price"] = float(price["current_price"])

    return prices

def _get_price_history_for_material(
    db: PostgresDB, material_id: int, start_date: str
) -> tuple[HistoricPrice]:
    """Получить историю цен на Материал по id начиная с даты."""
    p = {"start_date": start_date, "material_id": material_id}

    # p = {"material_id": material_id}
    historical_prices = db.select(
        sql_pg_queries["select_prices_material_for_target_periods"],
        p
    )
    result = [
        HistoricPrice(
            index_number=row["index_number"],
            base_price=float(row["base_price"]),
            current_price=float(row["current_price"]),
        )
        for row in historical_prices
    ]
    result.sort(reverse=False, key=lambda x: x.index_number)
    return result





def _materials_constructor(material: DictRow):
    # hp = _get_price_history_for_material(
    #     db, material["material_id"], PRICE_HISTORY_START_DATE
    #     )
    # print(hp)
    return Material(
        product_type=ProductType.MATERIAL,
        product_code=material["code"],
        product_description=material["description"],
        unit_measure=material["unit_measure"],
        #
        base_price=float(material["base_price"]),
        current_price=float(material["actual_price"]),
        #
        transport_code=material["transport_code"],
        transport_name=material["transport_name"],
        transport_base_price=float(material["transport_base_price"]),
        transport_current_price=float(material["transport_current_price"]),
        #
        storage_cost_rate=float(material["storage_rate"]),
        storage_cost_name=material["storage_name"],
        storage_cost_description=material["storage_description"],
    )


def _get_period_id_title(database: PostgresDB, period_pattern: str) -> int | None:
    """Получить id периода  и название по регулярному выражению названия."""
    query = sql_pg_queries["select_larix_period_by_regexp_title"]
    period = database.select(query, {"regexp_pattern": period_pattern})
    return period[0]["id"], clean_text(period[0]["title"]) if period else None


def get_materials_from_larix(period_pattern: str) -> tuple[Material, ...] | None:
    """Получить данные по материалам и историю цен на них для нужного периода и историю цен начиная с даты в config."""
    table = None

    with PostgresDB(ais_access) as db:
        larix_period = _get_period_id_title(db, period_pattern)
        if larix_period:
            larix_period_id, larix_period_title = larix_period
            period = MiniPeriod(
                period_larix_id=larix_period_id, period_name=larix_period_title
            )
            ic(period)
        else:
            return None
        query = sql_pg_queries["select_materials_for_period_id"]
        materials = db.select(query, {"period_id": period.period_larix_id})
        ic(len(materials))
        table = [_materials_constructor(material) for material in materials]
        if table:
            ic(DB_FILE)
            save_materials_support_db(DB_FILE, period, table)

        prices = _get_price_history_for_all_materials(db, PRICE_HISTORY_START_DATE)
        ic("история цен: ", len(prices))
        #
        # save_history_prices_support_duck_db(DUCK_DB_FILE, prices)
        # show_pivot_table_duck_db(DUCK_DB_FILE)
        #
    save_materials_history_prices_sqlite_db(DB_FILE, prices)
    create_materials_pivot_table_by_index_number(DB_FILE)

    return table if table else None


if __name__ == "__main__":
    ic()
    table = get_materials_from_larix(periods_pattern_name["supplement_72"])



    # ic(table[:2])
    # ic(len(table))
