from os import path

DUCK_DB_FILE_NAME = "Supporting_DB.duck_db"
DB_FILE_NAME = "Supporting_DB.sqlite3"
DB_FILE_PATH = r"C:\Users\kazak.ke\Documents\PythonProjects\Monitoring_Reports_larix\DB_support"
#

DUCK_DB_FILE = path.join(DB_FILE_PATH, DUCK_DB_FILE_NAME)
#
DB_FILE = path.join(DB_FILE_PATH, DB_FILE_NAME)
RAW_DATA_TABLE_NAME = "tblRawData"

CONFIG_FILE_NAME = "config_report.json"

TON_ORIGIN = "ТСН"     # TERRITORIAL OUTLAY NORMATIVE
PNWC_ORIGIN = "НЦКР"   # PRICE NORMATIVE FOR WORK COMPLEXES
POM_ORIGIN = "ПСМ"     # PROJECT OUTLAY MODULE
MONITORING_ORIGIN = "мониторинг"  # Monitoring of resource prices
EQUIPMENT_ORIGIN = "оборудование"  # Equipment

EQUIPMENTS_ORIGIN = "оборудование"
MONITORING_ORIGIN = "мониторинг"

ROUNDING = 2
MINIMUM_VALUE = 0E-2
PRICE_HISTORY_START_DATE = "2024-01-01"


CONSOLE_COLORS = {
    "YELLOW": "\u001b[38;5;11m",
    "RESET": "\u001b[0m",
    "RED": "\u001b[31m",
    "GREEN": "\u001b[32m",
}


PERIOD_PATTERNS = {
    "supplement": r"^\s*[Д|д]ополнение\s+\d+\s*$",
    "supplement_number": r"^\s*[Д|д]ополнение\s*(\d+)\s*$",
    "index": r"^\s*\d+\s+индекс\/дополнение\s+\d+\s+\(.+\)\s*$",
    "index_number_supplement_cmt": r"^\s*(\d+)\s+индекс\/дополнение\s+(\d+)\s+\((.*)\)\s*$",
    "monitoring": r"^\s*[М|м]ониторинг\s*(.*)\s\((\d+)\s+сборник\/дополнение\s+(\d+).*\)",
}


