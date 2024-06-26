from collections import namedtuple
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
from models import MonitoringMaterial, ProductType, MaterialIndexData, MonitoringPrice
from common_features import output_message_exit
from DB_support import get_monitoring_period_by_comment, get_index_period_by_number, get_supplement_period_by_number, get_period_by_id

WorkPeriods = namedtuple(
    typename="WorkPeriods",
    field_names=[
        "monitoring_period", "previous_monitoring_period", "index_period", "supplement_period"
    ],
    defaults=[ None, None, None, None],
)

MonitoringPrice.__annotations__ = {
    "monitoring_period": sqlite3.Row, 
    "previous_monitoring_period": sqlite3.Row, 
    "index_period": sqlite3.Row, 
    "supplement_period": sqlite3.Row
}



def _get_supplement_material(
    db: SQLiteDB, supplement_period_id: int, code: str
) -> sqlite3.Row | None:
    """Ищет в таблице материалов tblExpandedMaterial для дополнения и коду."""
    query = sql_sqlite_materials["select_expanded_material_by_code_period_id"]
    # ic(query)
    result = db.go_select(query, {"period_id": supplement_period_id, "code": code})
    if not result:
        output_message_exit(
            f"В 'tblExpandedMaterial' не найден материал {code!r}",
            f"для дополнения: {supplement_period_id=}",
        )
    return result[0]


def _get_monitoring_material_price_history(
    db: SQLiteDB, code: str, max_index_number: int
) -> list[MonitoringPrice] | None:
    """Получить историю цен мониторинга на материал по шифру и максимальному значению индекса."""
    result = db.go_select(
        sql_sqlite_monitoring["select_monitoring_history_price_for_code_and_index_less"],
        {"code": code, "index_number": max_index_number},
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


def _get_material_index_data(db: SQLiteDB, period_id: int, code: str) -> sqlite3.Row | None:
    """Ищет в таблице материалов tblHistoryPriceMaterials для period_id и code."""
    result = db.go_select(
        sql_sqlite_materials["select_history_price_materials_period_id_code"], 
        {"period_id": period_id, "product_code": code}
        )
    if not result:
        output_message_exit(
            f"В 'tblHistoryPriceMaterials' не найден материал {code!r}",
            f"для периода: {period_id=}",
        )
    return result[0]

def _material_constructor(
    db: SQLiteDB, work_periods: WorkPeriods, monitoring_material: sqlite3.Row
) -> MonitoringMaterial:
    """
    Ищет материал в tblExpandedMaterial по коду из отчета мониторинга и периоду дополнения.
    Получает историю цен и флаги доставки материал мониторинга по шифру.
    Заполняет объект Material."""
    material_code = monitoring_material["code"]
    # 
    previous_period_index_number = work_periods.previous_monitoring_period["index_number"]
    supplement_period_id = work_periods.supplement_period["id"]
    index_period_id = work_periods.index_period["id"]

    # найти материал из Дополнения supplement_period
    supplement_material = _get_supplement_material(
        db, supplement_period_id, material_code
    )
    # получить данные на материал для индексного периода
    materials_index_price = _get_material_index_data(
        db, index_period_id, material_code
    )
    # получить историю цен Мониторинга на материал для индексного периода
    monitoring_price_history = _get_monitoring_material_price_history(
        db, material_code, max_index_number=previous_period_index_number
    )
    index_period_material_data = MaterialIndexData(
        base_price = materials_index_price["base_price"],
        current_price = materials_index_price["current_price"],
        inflation_rate = materials_index_price["inflation_ratio"],
        #
        net_weight = materials_index_price["net_weight"],
        gross_weight = materials_index_price["gross_weight"],
        # 
        transport_code=materials_index_price["transport_code"],
        transport_name=materials_index_price["transport_name"],
        transport_base_price=materials_index_price["transport_base_price"],
        transport_current_price=materials_index_price["transport_current_price"],
        #
        storage_cost_rate=materials_index_price["storage_cost_rate"],
        storage_cost_name=materials_index_price["storage_cost_name"],
        storage_cost_description=materials_index_price["storage_cost_description"],
    )
    # ic(index_period_material_data)
    monitoring_model = MonitoringMaterial(
        product_type=ProductType.MATERIAL,
        product_code=supplement_material["code"],
        product_description=supplement_material["description"],
        unit_measure=supplement_material["unit_measure"],
        #         
        supplier_price=monitoring_material["supplier_price"],
        is_delivery_included=not monitoring_material["delivery"] == "False",
        monitoring_description=monitoring_material["description"],
        #
        monitoring_price_history=monitoring_price_history if monitoring_price_history else [],
        index_period_material_data=index_period_material_data
    )
    return monitoring_model


def _get_monitoring_materials_with_history_price(db_file: str, work_periods: WorkPeriods) -> list[MonitoringMaterial] | None:
    """
    Создает список материалов из файлу отчета мониторинга который загружен в таблицу tblMonitoringMaterialsReports. 
    В этой таблице содержатся данные из разных файлов каждый для своего периода
    Выбираются данные для указанного work_periods.monitoring_period.
    --
    История цен для каждого материала мониторинга грузится с начала истории 
    до предыдущего периода мониторинга work_periods.previous_monitoring_period.
    Данные о текущей цене материала берется из индексного периода для периода дополнения??.
    """
    with SQLiteDB(db_file) as db:
        # tblMonitoringMaterialsReports
        monitoring_period_id = work_periods.monitoring_period["id"]
        monitoring_materials = db.go_select(
            sql_sqlite_monitoring["select_monitoring_materials_for_period_id"],
            {"period_id": monitoring_period_id},
        )
        table = [
            _material_constructor(db, work_periods, monitoring_material)
            for monitoring_material in monitoring_materials
        ]
        ic(len(table))
    return table if table else None


def define_work_periods(db_file, monitoring_period_name: str) -> WorkPeriods:
    """ 
        Определяет периоды для загрузки данных мониторинга.
        --
        период мониторинга для файла отчета (для которого создан отчет),
        предыдущий период мониторинга, для загрузки истории цен мониторинга (верхняя граница),
        индексный период на материал для получения данных о текущей цене материала,
        период дополнения для загрузки данных о материале (ед.измерения, название...),
    """
    with SQLiteDB(db_file) as db:
        monitoring_period = get_monitoring_period_by_comment(db, monitoring_period_name)
        previous_monitoring_period = get_period_by_id(db, monitoring_period["previous_id"])
        supplement_period = get_supplement_period_by_number(db, monitoring_period["supplement_number"])
        index_period = get_index_period_by_number(db, monitoring_period["index_number"])
        # 
        return WorkPeriods(
            monitoring_period=monitoring_period, 
            previous_monitoring_period=previous_monitoring_period,
            index_period=index_period, 
            supplement_period=supplement_period
        )


def get_materials_monitoring_data(period_name: str, db_file: str) -> list[MonitoringMaterial] | None:
    """Получает список материалов мониторинга с историей цен."""
    operational_periods = define_work_periods(db_file, period_name)
    # 
    for x in operational_periods._fields:
        data = tuple(operational_periods._asdict()[x])
        ic(x, data)
    # выбрать материалы мониторинга с историей цен мониторинга и данными о цене из индексного периода
    table = _get_monitoring_materials_with_history_price(db_file, operational_periods)
    return table


if __name__ == "__main__":
    from config import DB_FILE

    ic()
    report_file = "april_materials_report.xlsx"
    period_name = "Апрель 2024"

    materials = get_materials_monitoring_data(period_name=period_name, db_file=DB_FILE)
    ic(len(materials))
    ic(materials[0].__dict__.keys())