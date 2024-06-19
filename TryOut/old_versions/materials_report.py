import sqlite3
from icecream import ic
from config import DB_FILE
from models import ExcelReport
from models import Material, MonitoringPrice, MonitoringMaterial, ProductType
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
        # история мониторинга
        "прошлый период транспорт включен",
        "нужна проверка",
        "мониторинг цена",  # monitoring price
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

    history_sizes = set([material.get_history_length() for material in table])
    max_history_len = max(history_sizes)
    ic(max_history_len, history_sizes)  #  {1, 4, 5}
    if max_history_len > view_history_depth:
        max_history_len = view_history_depth

    history_header = []
    #  найти материал с длинной историей и записать заголовок
    for material in table:
        if material.get_history_length() >= max_history_len:
            # ic(material.monitoring.price_history)
            # ic(material.monitoring.price_history[-max_history_len:])
            history_header = [
                x.period_name
                for x in material.monitoring.price_history[-max_history_len:]
            ]
            # ic(history_header)
            break
    final_header = [*header[:4], *history_header, *header[4:], *header_calculated]
    return final_header, max_history_len


def _get_supplement_material(db: SQLiteDB, supplement_name: str, code: str)-> sqlite3.Row | None:
    """Ищет в таблице материалов tblExpandedMaterial для дополнения и коду."""
    query = sql_sqlite_materials["select_expanded_material_by_code_period_name"]
    # ic(query)
    result = db.go_select(
        query, {"period_name": supplement_name, "code": code}
    )
    if not result:
        output_message_exit(
            f"В 'tblExpandedMaterial' не найден материал {code!r}",
            f"для дополнения  {supplement_name!r}",
        )
    return result[0]

def _get_monitoring_material_price_history(
    db: SQLiteDB, code: str
) -> list[MonitoringPrice] | None:
    """Получить историю цен мониторинга на материал по шифру."""
    result = db.go_select(
        sql_sqlite_monitoring["select_monitoring_history_price_for_code"],
        {"code": code},
    )
    if not result:
        return None
        # output_message_exit(
        #     "В 'tblMonitoringHistoryPrices' не найдены цены", f"для {code!r}"
        # )
    history = [
        MonitoringPrice(
            period_name=row["period_name"],
            index_number=row["index_number"],
            price=row["price"],
            delivery=row["delivery"] == 1,
        )
        for row in result
    ]
    history.sort(reverse=False, key=lambda x: x.index_number)
    return history


def _material_constructor(
    db: SQLiteDB,
    supplement_period: sqlite3.Row,
    monitoring_material: sqlite3.Row,
    monitoring_period_name: int,
) -> Material:
    """
    Ищет материал в tblExpandedMaterial по коду из отчета мониторинга и периоду дополнения.
    Получает историю цен и флаги доставки материал мониторинга по шифру.
    Заполняет объект Material."""
    supplement_material = _get_supplement_material(
        db, supplement_period["name"], monitoring_material["code"]
    )
    price_history = _get_monitoring_material_price_history(
        db, monitoring_material["code"]
    )

    monitoring_data = MonitoringMaterial(
        code=monitoring_material["code"],
        period_name=monitoring_period_name,
        supplier_price=monitoring_material["supplier_price"],
        is_transport_included=bool(monitoring_material["delivery"]),
        description=monitoring_material["description"],
        #
        price_history=price_history if price_history else [],
    )

    material = Material(
        product_type=ProductType.MATERIAL,
        product_code=supplement_material["code"],
        product_description=supplement_material["description"],
        unit_measure=supplement_material["unit_measure"],
        #
        net_weight=supplement_material["net_weight"],
        gross_weight=supplement_material["gross_weight"],
        base_price=supplement_material["base_price"],
        current_price=supplement_material["current_price"],
        #
        transport_code=supplement_material["transport_code"],
        transport_name=supplement_material["transport_name"],
        transport_base_price=supplement_material["transport_base_price"],
        transport_current_price=supplement_material["transport_current_price"],
        #
        storage_cost_rate=supplement_material["storage_cost_rate"],
        storage_cost_name=supplement_material["storage_cost_name"],
        storage_cost_description=supplement_material["storage_cost_description"],
        monitoring=monitoring_data,
    )
    return material


def _get_monitoring_materials_with_history_price(
        db_file: str,
        monitoring_period: sqlite3.Row,
        supplement_period: sqlite3.Row,
) -> list[Material] | None:
    """Создать список материалов по отчету мониторинга. """
    with SQLiteDB(db_file) as db:
        # tblMonitoringMaterialsReports
        monitoring_materials = db.go_select(
            sql_sqlite_monitoring["select_monitoring_materials_for_period_id"],
            {"period_id": monitoring_period["id"]},
        )
        table = [
            _material_constructor(
                db, supplement_period, monitoring_material, monitoring_period["name"]
            )
            for monitoring_material in monitoring_materials
        ]
    return table if table else None

def _get_monitoring_period_by_comment(db_file: str, period_comment: str) -> sqlite3.Row | None:
    """Возвращает период мониторинга по его комментарию."""
    with SQLiteDB(db_file) as db:
        period = db.go_select(
            sql_sqlite_periods["select_monitoring_by_comment"],
            {"monitoring_comment": period_comment}
            )
        if not period:
            output_message_exit(
                "В таблице 'tblPeriods'", f"Не найден период мониторинга: {period_name!r}"
            )
        return period[0]

def _get_supplement_period_by_number(db_file: str, supplement_number: int) -> sqlite3.Row | None:
    """Возвращает период дополнения по номеру дополнения."""
    with SQLiteDB(db_file) as db:
        period = db.go_select(
            sql_sqlite_periods["select_ton_supplement_by_number"],
            {"supplement_number": supplement_number},
        )
        if not period:
            output_message_exit(
                "В таблице 'tblPeriods'", f"Не найден период дополнения: {supplement_number}"
            )
        return period[0]


def create_material_monitoring_report(
    period_name: str,
    report_file_name: str,
    sheet_name: str,
    view_history_depth: int,
    db_file: str
) -> int | None:
    """Напечатать отчет по мониторингу материалов"""
    monitoring_period = _get_monitoring_period_by_comment(db_file, period_name)
    supplement_number = monitoring_period["supplement_number"]
    supplement_period = _get_supplement_period_by_number(db_file, supplement_number)
    #
    table = _get_monitoring_materials_with_history_price(
        db_file, monitoring_period, supplement_period
    )
    ic(len(table))

    with ExcelReport(report_file_name) as file:
        sheet = file.get_sheet(sheet_name, 0)
        file.delete_sheets(["Sheet", "Таблица 1"])
        #
        file.workbook.active = sheet
        #

        header, max_history_len = _header_create(table, view_history_depth)
        ic(max_history_len, header)
        file.write_header(sheet.title, header)
        row = 2
        for i, material in enumerate(table):
            value_row = _material_row_create(material, row, max_history_len)
    #         value_row[0] = i + 1
    #         file.write_row(sheet_name, value_row, row)
    #         file.write_material_format(sheet_name, row, max_history_len)
    #         row += 1
    #     ic()
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