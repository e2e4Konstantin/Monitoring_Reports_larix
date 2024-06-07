
from DB_support.sql_sqlite_materials import sql_sqlite_materials
from DB_support.db_config import SQLiteDB
from models import Material, MiniPeriod

def _prepare_material_data(material: Material, mini_period: MiniPeriod) -> dict:
    """
    Подготовить словарь с данными о материале и периоде.
    """
    period_data = mini_period._asdict()
    material_data = material.__dict__
    return {**period_data, **material_data}


def save_materials_support_db(
    db_file: str,
    period: MiniPeriod,
    list_of_materials: list[Material] = None
):
    """
    Сохранить список объектов Material в SQLite db_file.
    """
    with SQLiteDB(db_file) as db:
        db.go_execute(sql_sqlite_materials["delete_table_expanded_material"])
        db.go_execute(sql_sqlite_materials["create_table_expanded_material"])
        db.go_execute(sql_sqlite_materials["create_index_expanded_material"])
        # 
        for material in list_of_materials:
            data = _prepare_material_data(material, period)
            db.go_execute(
                sql_sqlite_materials["insert_row_expanded_material"], data
            )

