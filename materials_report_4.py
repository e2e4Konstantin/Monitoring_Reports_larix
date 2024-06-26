import numpy as np
from icecream import ic

from report_tools import (
    get_materials_monitoring_data,
    create_header,
    create_line_material,
)
from models import ExcelReport
# from models import Material
def calculate_abbe_criterion(signal):
    """Вычисляет Abbe criterion для последовательности значений."""
    if len(signal) <= 3:
        return 0
    differences = np.diff(signal) ** 2
    squared_differences = np.sum(differences)
    return np.sqrt(squared_differences / (len(signal) - 1))



def monitoring_price_history_report(
    last_period_name: str, report_file_name: str, sheet_name: str, db_file: str
):
    """Вывести отчет по ценам мониторинга материалов."""
    monitoring_materials = get_materials_monitoring_data(last_period_name, db_file)
    history_sizes = set([material.get_history_length() for material in monitoring_materials])
    max_history_len = max(history_sizes)

    for material in monitoring_materials:
        if material.get_history_length() == max_history_len:
            history_header = ["\n".join(x.period_name.split()) for x in material.monitoring_price_history]
            break
    history_header = ["No", "шифр", *history_header, "abbe criterion", "mean", "std"]
    # ic(history_header)
    row = 2
    with ExcelReport(report_file_name) as file:
        sheet = file.get_sheet(sheet_name)
        file.write_header(sheet.title, history_header)
        
        for i, material in enumerate(monitoring_materials):
            signal = [item.price for item in material.monitoring_price_history]
            abc = calculate_abbe_criterion(signal)
            ic(abc)
        #     price_row = _create_history_price_row(material, max_history_len)
        #     price_row = [i + 1, material.code, *price_row]
        #     sheet.append(price_row)
        #     row += 1

def create_material_monitoring_report(
    period_name: str,
    report_file_name: str,
    sheet_name: str,
    view_history_depth: int,
    db_file: str
) -> int | None:
    """Напечатать отчет по мониторингу материалов"""
    monitoring_materials  = get_materials_monitoring_data(period_name, db_file)
    ic(len(monitoring_materials))

    with ExcelReport(report_file_name) as file:
        sheet = file.get_sheet(sheet_name, 0)
        file.delete_sheets(["Sheet", "Таблица 1"])
        file.workbook.active = sheet
        #
        header, max_history_len = create_header(
            monitoring_materials, view_history_depth
        )
        # ic(max_history_len, header)
        file.write_header(sheet.title, header)
        row = 2
        for i, material in enumerate(monitoring_materials[:5]): # [:5]
            value_row = create_line_material(material, row, max_history_len)
            value_row[0] = i + 1
            file.write_row(sheet_name, value_row, row)
            file.write_material_format(sheet_name, row, max_history_len)
            row += 1
    return 0



if __name__ == "__main__":
    from config import DB_FILE

    ic()
    # 1. создать БД create_new_support_db.py
    # 2. прочитать данные для периода read_prepare_larix_data.py
    # 3. читать исходный файл от мониторинга load_monitoring_file.py

    report_file = "may_2024_materials_report.xlsx"
    sheet_name = "materials"
    period_name = "Май 2024"

    # create_material_monitoring_report(
    #     period_name=period_name,
    #     report_file_name=report_file,
    #     sheet_name=sheet_name,
    #     view_history_depth=4,
    #     db_file=DB_FILE
    # )

    monitoring_price_history_report(
        last_period_name=period_name,
        report_file_name=report_file,
        sheet_name="monitoring_price_history ",
        db_file=DB_FILE
    )