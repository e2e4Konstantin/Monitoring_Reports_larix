from icecream import ic
import psycopg2
from psycopg2.extras import DictRow

#
from config import PostgresDB, ais_access, PRICE_HISTORY_START_DATE
from models import Material, ProductType, HistoricPrice
from sql_queries import sql_pg_queries


def _get_price_history_for_material(
    db: PostgresDB, material_id: int, date_start: str
) -> tuple[HistoricPrice]:
    """Получить историю цен на материал по id начиная с даты."""
    # p = ({"date_start": date_start, "material_id": material_id},)

    p = {"material_id": material_id}
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
    return Material(
        product_type=ProductType.MATERIAL,
        product_code=material["code"],
        product_description=material["description"],
        unit_measure=material["unit_measure"],
        #
        base_price=material["base_price"],
        current_price=material["actual_price"],
        #
        transport_code=material["transport_code"],
        transport_name=material["transport_name"],
        transport_base_price=material["transport_base_price"],
        transport_current_price=material["transport_current_price"],
        #
        storage_cost_rate=material["storage_rate"],
        storage_cost_name=material["storage_name"],
        storage_cost_description=material["storage_description"],
    )







def get_materials_from_larix() -> tuple[Material, ...] | None:
    """."""
    table = None
    with PostgresDB(ais_access) as db:
        materials = db.select(
            sql_pg_queries["select_materials_for_period"],
            {"regexp_pattern": "^\s*Дополнение\s*72\s*$"}
        )
        ic(len(materials))
        for material in materials:
            obj_material = _materials_constructor(material)
            ic(type(db))
            hp = _get_price_history_for_material(
                db, material["material_id"], PRICE_HISTORY_START_DATE
                )
            print(hp)

        # table = [
        #     _materials_constructor(material)
        #     for material in materials
        # ]
    return table if table else None


if __name__ == "__main__":
    ic()
    table = get_materials_from_larix()
    ic(table[:2])
    ic(len(table))
