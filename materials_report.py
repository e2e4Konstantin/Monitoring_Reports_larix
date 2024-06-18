import sqlite3
from icecream import ic
from config import DB_FILE, ExcelReport
from models import Material
from DB_support import (
    SQLiteDB,
    sql_sqlite_periods,
    sql_sqlite_monitoring,
    sql_sqlite_queries,
    sql_sqlite_materials,
    create_new_monitoring_period,
)

from common_features import output_message_exit


def _header_create(table: list[Material], view_history_depth: int) -> str:
    header = [
        "No",
        "шифр",
        "название",
        "базовая стоимость",
        "текущий индекс",  # actual index
        "текущая цена",  # actual price
        "мониторинг индекс",  # monitoring index
        "мониторинг цена",  # monitoring price
        #
        "история транспорт включен",  # history freight included
        "история без транспорта",  # history freight not included
        "нужна проверка",  # history check
        #
        "транспорт включен",  # transport flag
        "шифр транспорта",  # transport code
        "транспорт базовая цена",  # transport base price
        "транспорт коэффициент",  # transport numeric ratio
        "транспорт текущая цена",  # transport actual price
        #
        "вес брутто",  # gross weight
    ]
    header_calculated = [
        ".",
        "стоимость перевозки",
        "цена для загрузки",
        "предыдущий индекс",
        "текущий индекс",
        "рост абс.",
        "рост %",
        ".",
        "критерий разниц пар",
        "абс.",
        "внимание",
        "процент рост/падение",
    ]
    history_sizes = set([material.len_history for material in table])
    ic(history_sizes)  #  {1, 4, 5}
    max_history_len = max(history_sizes)
    history_header = []
    #  найти материал с длинной историей и записать заголовок
    for material in table:
        if material.len_history == max_history_len:
            # ic(material)
            history_header = [x.history_index for x in material.history]
            #
            if max_history_len > view_history_depth:
                history_header = history_header[-view_history_depth:]
                max_history_len = len(history_header)
            break
    final_header = [*header[:4], *history_header, *header[4:], *header_calculated]
    return final_header, max_history_len

def _materials_constructor(
    db: SQLiteDB, monitoring_index_num: int, supplement_period_name: str, row: sqlite3.Row, history_depth: int
) -> Material:
    # tblExpandedMaterial
    supplement_material = db.go_select(
        sql_sqlite_materials["select_expanded_material_by_code_period_name"],
        {"period_name": supplement_period_name, "code": row["code"]},
    )
    if not supplement_material:
        output_message_exit(f"Не удалось получить информацию о материале {row['code']}")

    material = Material(
        code=supplement_material["code"],
        name=supplement_material["description"],
        base_price=supplement_material["base_price"],
        actual_price=supplement_material["actual_price"],
        transport_code=supplement_material["transport_code"],
        transport_base_price=supplement_material["transport_base_price"],
        transport_actual_price=supplement_material["transport_current_price"],
        !!!!!!!!!!!
        gross_weight=supplement_material["gross_weight"],
        #
        # index_num=row["index_num"],
        #
        monitoring_index=monitoring_index_num,
        monitoring_price=row["supplier_price"],
        transport_flag=bool(row["transport_flag"]),
        #
        history_freight_included=row["history_freight_included"],
        history_freight_not_included=row["history_freight_not_included"],


        history_check=row["history_check"],
        #



        #
        history=_get_material_price_history(db, row["ID_tblMaterial"], history_depth),
    )
    return material


def _get_monitoring_materials_with_history_price(
        period: sqlite3.Row, db_file: str, history_depth: int
) -> list[Material] | None:
    """Создать список материалов по отчету мониторинга
    для периода period_id с глубиной истории history_depth.
    """
    with SQLiteDB(db_file) as db:
        # tblMonitoringMaterialsReports
        monitoring_materials = db.go_select(
            sql_sqlite_monitoring["select_monitoring_materials_for_period_id"],
            {"period_id": period["id"]},
        )
        # найти период дополнения для периода мониторинга
        supplement_number = period["supplement_number"]
        supplement_period = db.go_select(
            sql_sqlite_periods["select_supplement_by_number"],
            {"supplement_number": supplement_number},
        )
        supplement_period_id = supplement_period["id"]

        table = [
            _materials_constructor(db, supplement_period_id, material, history_depth)
            for material in monitoring_materials
        ]
    return table if table else None

def get_period_by_comment(db_file: str, period_comment: str) -> int | None:
    """Возвращает период мониторинга по его комментарию."""
    with SQLiteDB(db_file) as db:
        query = sql_sqlite_periods["select_monitoring_by_comment"]
        period = db.go_select(query, {"monitoring_comment": period_comment})
    return period[0] if period else None


def create_material_monitoring_report(
    period_name: str,
    report_file_name: str,
    sheet_name: str,
    view_history_depth: int,
    db_file: str
) -> int | None:
    """Напечатать отчет по мониторингу материалов"""
    period = get_period_id_by_comment(db_file, period_name)
    if not period_id:
        message = f"В таблице 'tblPeriods'"
        output_message_exit(message, f"Не найден период {period_name!r}")
    #
    table = _get_monitoring_materials_with_history_price(period, db_file, view_history_depth)
    #
    with ExcelReport(report_file_name) as file:
        sheet = file.get_sheet(sheet_name, 0)
        file.delete_sheets(["Sheet", "Таблица 1"])
        #
        file.workbook.active = sheet
        #
        header, max_history_len = _header_create(table, view_history_depth)
        file.write_header(sheet.title, header)

        row = 2
        for i, material in enumerate(table):
            value_row = _material_row_create(material, row, max_history_len)
            value_row[0] = i + 1
            file.write_row(sheet_name, value_row, row)
            file.write_material_format(sheet_name, row, max_history_len)
            row += 1
        ic()
        return 0



if __name__ == "__main__":
    ic()
    # 1. создать БД create_new_support_db.py
    # 2. прочитать данные для периода read_prepare_larix_data.py
    # 3. читать исходный файл от мониторинга load_monitoring_file.py

    report_file = "april_materials_report.xlsx"
    sheet_name = "materials"
    period_name = "Апрель 2024"

    create_material_monitoring_report(
        period_name=period_name,
        report_file_name=report_file,
        sheet_name=sheet_name,
        view_history_depth=4,
        db_file=DB_FILE
    )