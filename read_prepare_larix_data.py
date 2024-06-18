from icecream import ic

from config import (
    periods_pattern_name,
    PRICE_HISTORY_START_DATE,
    DB_FILE,
    PERIOD_CSV_FILE,
)


from data_extraction import (
    get_periods_from_larix,
    get_materials_from_larix,
    get_history_prices_materials_from_larix,
    get_monitoring_materials_from_larix,
)


if __name__ == "__main__":
    ic("Читаем и подготавливаем данные из larix")
    get_periods_from_larix(DB_FILE, PERIOD_CSV_FILE)
    get_materials_from_larix(periods_pattern_name["supplement_72"])
    get_history_prices_materials_from_larix(PRICE_HISTORY_START_DATE)
    get_monitoring_materials_from_larix(DB_FILE, PRICE_HISTORY_START_DATE)