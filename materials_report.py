
from icecream import ic
from report_tools import (
    get_materials_monitoring_data,
    create_header,
    create_line_material,
)
from models import ExcelReport
# from models import Material



def create_material_monitoring_report(
    period_name: str,
    report_file_name: str,
    sheet_name: str,
    view_history_depth: int,
    db_file: str
) -> int | None:
    """Напечатать отчет по мониторингу материалов"""
    materials_monitoring = get_materials_monitoring_data(period_name, db_file)
    ic(len(materials_monitoring))

    with ExcelReport(report_file_name) as file:
        sheet = file.get_sheet(sheet_name, 0)
        file.delete_sheets(["Sheet", "Таблица 1"])
        #
        file.workbook.active = sheet
        #

        header, max_history_len = create_header(
            materials_monitoring, view_history_depth
        )
        ic(max_history_len, header)
        file.write_header(sheet.title, header)
        row = 2
        for i, material in enumerate(materials_monitoring):
            ic(i)
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