from icecream import ic
import numpy as np
from models import ExcelReport
from report_tools.get_data_for_report import get_materials_monitoring_data

from models import MonitoringMaterial


def _get_price_and_delivery_ranges(material: MonitoringMaterial = None, period_names: list[str] = None) -> tuple[list[float], list[bool]] | None:
    """Возвращает список цен и флагов доставки для заданного материала. Для каждого периода из списка."""
    if not material or not period_names:
        return None
    prices, delivery_flags = [], []
    for period_name in period_names:
        for price in material.monitoring_price_history:
            if price.period_name == period_name:
                prices.append(price.price)
                delivery_flags.append(price.delivery)
                break
        else:
            prices.append(" ")
            delivery_flags.append(None)
    return prices, delivery_flags

def create_monitoring_price_history_report(
    last_period_name: str, report_file_name: str, sheet_name: str, db_file: str
):
    """Вывести отчет по ценам мониторинга материалов."""
    monitoring_materials = get_materials_monitoring_data(last_period_name, db_file)
    history_sizes = set([material.get_history_length() for material in monitoring_materials])
    max_history_len = max(history_sizes)

    for material in monitoring_materials:
        if material.get_history_length() == max_history_len:
            # period_names = ["\n".join(x.period_name.split()) for x in material.monitoring_price_history]
            period_names = [price.period_name for price in material.monitoring_price_history]
            break
    modern_period_names = ["\n".join(names.split()) for names in period_names]
    history_header = ["No", "шифр",  "дельта",  "название", "уточнение", *modern_period_names, "доставка", "mean", "std", "diff"]        
    # ic(history_header)
    # row = 2
    with ExcelReport(report_file_name) as file:
        sheet = file.get_sheet(sheet_name)
        file.workbook.active = sheet
        # 
        # test = ["1.7-11-75", "1.7-11-76", "1.7-14-630", "1.23-4-308", "1.1-1-764"]
        file.write_header(sheet.title, history_header)
        for row, material in enumerate(monitoring_materials, start=2):
            code = material.code
            # if code not in test:
            #     continue
            title = material.description
            name = material.monitoring_description
            price_range, delivery_range = _get_price_and_delivery_ranges(material, period_names)
            if len(material.monitoring_price_history) > 1:
                signal = [item.price for item in material.monitoring_price_history]
                mean, std = float(np.mean(signal)), float(np.std(signal))
                mean_log_diff = float(np.mean(np.square(np.diff(np.log(signal)))))
            else:
                signal, mean, std, mean_log_diff  = 0, float(np.mean(signal)), 0, 0
            # print(delivery_range)
            true_count = delivery_range.count(True)
            false_count = delivery_range.count(False)
            # ic(true_count, false_count)
            delta = abs(true_count - false_count)
            delta = delta if delta < max_history_len else 0
            # 
            display_line = {
                "row": row-1, "code": code, "delta": delta, "title": title, "name": name, 
                "price_range": price_range, "mean": mean, "std": std, "delivery_range": delivery_range, "mean_log_diff": mean_log_diff
            }
            file.write_material_history_line(sheet_name, display_line, row)

if __name__ == "__main__":
    from config import DB_FILE

    ic()
    report_file = "may_2024_materials_report.xlsx"
    
    create_monitoring_price_history_report(
        last_period_name="Май 2024",
        report_file_name=report_file,
        sheet_name="monitoring_price_history ",
        db_file=DB_FILE
    )