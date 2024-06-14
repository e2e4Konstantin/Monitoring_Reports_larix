import pandas
from icecream import ic
from config import DB_FILE

def parse_monitoring_material_file(data: dict[str: str]) -> int | None:
    """Разбирает файл с ценами на материалы для мониторинга."""
    source_file = data["src_file"]
    result_file = data["result_file"]
    sheet_name = data["sheet_name"]

    result = get_monitoring_material_data(source_file, sheet_name)
    df = pandas.DataFrame(result, columns=["code", "price", "delivery", "description"])
    df.to_csv(result_file, sep=",", index=False)


def last_period_main(db_name: str, file_name: str, sheet_name: str):
    """создает основной отчет и историю цен материалов"""
    ic()
    table = _get_materials_with_monitoring(db_name, history_depth=10)
    # ic(len(table))
    # ic(table[0])
    # # основной отчет
    # _modern_materials_monitoring_report_output(
    #     table, view_history_depth=3, sheet_name=sheet_name, file_name=file_name
    # )
    # # история цен
    # _material_price_history_report_output(
    #     table, sheet_name="price materials history", file_name=file_name
    # )


if __name__ == "__main__":
    ic()
    # исходные данные
    may_2024 = ("5_Отчет апрель 2024.xlsx", 72, 212, "приложение А"),

    file_name = "larix_materials_report.xlsx"
    sheet_name = "materials"


    # создаем основной отчет и историю цен материалов
    last_period_main(DB_FILE, file_name, sheet_name)