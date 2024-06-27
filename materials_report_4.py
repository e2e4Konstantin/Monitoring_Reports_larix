
from icecream import ic

from report_tools import create_material_monitoring_report, create_monitoring_price_history_report


if __name__ == "__main__":
    from config import DB_FILE

    ic()
    # 1. создать БД create_new_support_db.py
    # 2. прочитать данные для периода read_prepare_larix_data.py
    # 3. читать исходный файл от мониторинга load_monitoring_file.py

    report_file = "may_2024_materials_report.xlsx"
    period_name = "Май 2024"

    create_material_monitoring_report(
        period_name=period_name,
        report_file_name=report_file,
        sheet_name="materials",
        view_history_depth=4,
        db_file=DB_FILE
    )

    create_monitoring_price_history_report(
        last_period_name=period_name,
        report_file_name=report_file,
        sheet_name="monitoring_price_history ",
        db_file=DB_FILE
    )