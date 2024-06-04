from config.periods_config import SupplementPeriod, IndexPeriod

ROUNDING = 2

TON_ORIGIN = "ТСН"     # TERRITORIAL OUTLAY NORMATIVE
PNWC_ORIGIN = "НЦКР"   # PRICE NORMATIVE FOR WORK COMPLEXES
POM_ORIGIN = "ПСМ"     # PROJECT OUTLAY MODULE

EQUIPMENTS_ORIGIN = "оборудование"
MONITORING_ORIGIN = "мониторинг"

MAIN_RECORD_CODE = "0.0"
DEFAULT_RECORD_CODE = "0.0-0-0"

LOCATIONS = ("home", "office")

CONFIG_FILE_NAME = 'config_report.json'

MINIMUM_VALUE = 0E-2

PERIODS = {
    "supplement_72": SupplementPeriod(
        name="Дополнение 72",
        period_title="Дополнение 72",
        period_id=167085727,
        parent_id=166954793,
        regex_pattern=r"^\s*Дополнение\s*72\s*$",
        #
        supplement_number=72,
    ),
    "supplement_71": SupplementPeriod(
        name="Дополнение 71",
        period_title="Дополнение 71",
        period_id=166954793,
        parent_id=152472566,
        regex_pattern=r"^\s*Дополнение\s*71\s*$",
        #
        supplement_number=71,
    ),
    "supplement_70": SupplementPeriod(
        name="Дополнение 70",
        period_title="Дополнение 70",
        period_id=152472566,
        parent_id=151427079,
        regex_pattern=r"^\s*Дополнение\s*70s*$",
        #
        supplement_number=70,
    ),
    "supplement_69": SupplementPeriod(
        name="Дополнение 69",
        period_title="Дополнение 69",
        period_id=151427079,
        parent_id=None,
        regex_pattern=r"^\s*Дополнение\s*69s*$",
        #
        supplement_number=69,
    ),

}
