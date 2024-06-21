import sqlite3
from icecream import ic
#
from DB_support import (
    SQLiteDB,
    sql_sqlite_periods,
    sql_sqlite_monitoring,
    sql_sqlite_queries,
    sql_sqlite_materials,
    create_new_monitoring_period,
)
from models import Material, MonitoringPrice, MonitoringMaterial, ProductType
from common_features import output_message_exit



def _get_monitoring_period_by_comment(
    db_file: str, period_comment: str
) -> sqlite3.Row | None:
    """Возвращает период мониторинга по его комментарию."""
    with SQLiteDB(db_file) as db:
        period = db.go_select(
            sql_sqlite_periods["select_monitoring_by_comment"],
            {"monitoring_comment": period_comment},
        )
        if not period:
            output_message_exit(
                "В таблице 'tblPeriods'",
                f"Не найден период мониторинга: {period_comment!r}",
            )
        return period[0]


def _get_supplement_period_by_number(
    db_file: str, supplement_number: int
) -> sqlite3.Row | None:
    """Возвращает период дополнения по номеру дополнения."""
    with SQLiteDB(db_file) as db:
        period = db.go_select(
            sql_sqlite_periods["select_ton_supplement_by_number"],
            {"supplement_number": supplement_number},
        )
        if not period:
            output_message_exit(
                "В таблице 'tblPeriods'",
                f"Не найден период дополнения: {supplement_number}",
            )
        return period[0]


def _get_supplement_material(
    db: SQLiteDB, supplement_name: str, code: str
) -> sqlite3.Row | None:
    """Ищет в таблице материалов tblExpandedMaterial для дополнения и коду."""
    query = sql_sqlite_materials["select_expanded_material_by_code_period_name"]
    # ic(query)
    result = db.go_select(query, {"period_name": supplement_name, "code": code})
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
        is_transport_included=not monitoring_material["delivery"] == "False",
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
    """Создать список материалов по отчету мониторинга."""
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


def get_materials_monitoring_data(period_name: str, db_file: str) -> list[Material] | None:
    """Получает список материалов мониторинга с историей цен."""
    monitoring_period = _get_monitoring_period_by_comment(db_file, period_name)
    supplement_number = monitoring_period["supplement_number"]
    supplement_period = _get_supplement_period_by_number(db_file, supplement_number)
    #
    table = _get_monitoring_materials_with_history_price(
        db_file, monitoring_period, supplement_period
    )
    return table


if __name__ == "__main__":
    from config import DB_FILE

    ic()
    report_file = "april_materials_report.xlsx"
    period_name = "Апрель 2024"

    materials = get_materials_monitoring_data(period_name=period_name, db_file=DB_FILE)
    ic(len(materials))
    ic(materials[0].__dict__.keys())