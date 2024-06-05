from icecream import ic
import psycopg2
from psycopg2.extras import DictRow

#
from config import PostgresDB, ais_access
from models import Material, ProductType
from sql_queries import sql_pg_queries

def _materials_constructor(material: DictRow):
    return Material(
        product_type=ProductType.MATERIAL,
        product_code = material["code"],
        product_description=material["description"],
        unit_measure=material["unit_measure"],
        #
        material_base_price=material["base_price"],
        material_price=material["actual_price"],
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
        table = [
            _materials_constructor(material)
            for material in materials
        ]
    return table if table else None


if __name__ == "__main__":
    ic()
    table = get_materials_from_larix()
    ic(table[:5])
    ic(len(table))
