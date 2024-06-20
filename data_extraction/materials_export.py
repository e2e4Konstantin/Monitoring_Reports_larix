from psycopg2.extras import DictRow
from DB_support.sql_sqlite_materials import sql_sqlite_materials
from DB_support.sql_sqlite_periods import sql_sqlite_periods
from DB_support.db_config import SQLiteDB
# from models import Material, MiniPeriod
import sqlite3
from common_features import code_to_number, output_message_exit


def _get_sqlite_period_by_larix_period_id(db_file: str, larix_period_id: int) -> sqlite3.Row | None:
    """ Возвращает данные о периоде по larix_period_id. """
    with SQLiteDB(db_file) as db:
        result = db.go_select(
            sql_sqlite_periods["select_by_larix_id"],
            {"larix_period_id": larix_period_id},
        )
        return result[0] if result else None


def _prepare_material_data(
    db_file: str, material: DictRow, larix_period_id: int, period: sqlite3.Row
) -> dict:
    """ Подготовить словарь с данными о материале и периоде. """
    data = {
        "period_larix_id": larix_period_id,
        "period_name": period["name"],
        "period_id": period["id"],
        "product_type": material["type"],
        "code": material["code"],
        "description": material["description"],
        "unit_measure": material["unit_measure"],
        "digit_code": code_to_number(material["code"]),
    }
    return data


def save_materials_support_db(
    db_file: str, larix_period_id: int, materials: list[DictRow] = None
):
    """
    Сохранить список объектов Material в SQLite db_file.
    """
    with SQLiteDB(db_file) as db:
        db.go_execute(sql_sqlite_materials["delete_table_expanded_material"])
        db.go_execute(sql_sqlite_materials["create_table_expanded_material"])
        db.go_execute(sql_sqlite_materials["create_index_expanded_material"])
        #
        period = _get_sqlite_period_by_larix_period_id(db_file, larix_period_id)
        if not period:
            output_message_exit(
                "В таблице 'tblPeriods'", f"Не найден период: {larix_period_id=}"
            )
        for material in materials:
            data = _prepare_material_data(db_file, material, larix_period_id, period)
            db.go_execute(
                sql_sqlite_materials["insert_row_expanded_material"], data
            )

