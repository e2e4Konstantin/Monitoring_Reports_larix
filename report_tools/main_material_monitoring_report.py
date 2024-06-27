
from icecream import ic


from models import ExcelReport
from report_tools.get_data_for_report import get_materials_monitoring_data
from report_tools.create_header import create_header
from report_tools.create_line_material import create_line_material

def create_material_monitoring_report(
    period_name: str,
    report_file_name: str,
    sheet_name: str,
    view_history_depth: int,
    db_file: str
) -> int | None:
    """Напечатать основной отчет по мониторингу материалов по данным из файла"""
    monitoring_materials  = get_materials_monitoring_data(period_name, db_file)
    ic(len(monitoring_materials), sheet_name)

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
        
        for row, material in enumerate(monitoring_materials, start=2): # [:5]
            value_row = create_line_material(material, row, max_history_len)
            value_row[0] = row - 1
            file.write_row(sheet_name, value_row, row)
            file.write_material_format(sheet_name, row, max_history_len)
    return 0



if __name__ == "__main__":
    from config import DB_FILE
    ic()
    
    report_file = "may_2024_materials_report.xlsx"

    create_material_monitoring_report(
        period_name="Май 2024",
        report_file_name=report_file,
        sheet_name="materials",
        view_history_depth=4,
        db_file=DB_FILE
    )
