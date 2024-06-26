from icecream import ic
from DB_support.db_config import SQLiteDB
from config import (
    DB_FILE,
    TON_ORIGIN,
    PNWC_ORIGIN,
    POM_ORIGIN,
    MONITORING_ORIGIN,
    EQUIPMENT_ORIGIN,
)
from DB_support.sql_sqlite_directories import sql_sqlite_directories
from DB_support.sql_sqlite_periods import sql_sqlite_periods
from DB_support.sql_sqlite_monitoring import sql_sqlite_monitoring
from DB_support.sql_sqlite_materials import sql_sqlite_materials


def _create_periods_environment(db: SQLiteDB) -> int:
    """Создать инфраструктуру для Справочников. """
    db.go_execute(sql_sqlite_periods["delete_table_periods"])
    db.go_execute(sql_sqlite_periods["delete_index_periods"])
    db.go_execute(sql_sqlite_periods["delete_view_periods"])
    #
    db.go_execute(sql_sqlite_periods["create_table_periods"])
    db.go_execute(sql_sqlite_periods["create_index_periods"])
    db.go_execute(sql_sqlite_periods["create_view_periods"])
    return 0


def _create_directory_environment(db: SQLiteDB) -> int:
    """Инфраструктура для Периодов."""
    db.go_execute(sql_sqlite_directories["delete_table_items"])
    db.go_execute(sql_sqlite_directories["delete_index_items"])
    #
    db.go_execute(sql_sqlite_directories["create_table_items"])
    db.go_execute(sql_sqlite_directories["create_main_index_directory"])
    db.go_execute(sql_sqlite_directories["create_chain_index_directory"])
    return 0

def _create_monitoring_environment(db: SQLiteDB) -> int:
    """Инфраструктура для отчётов файлов мониторинга."""
    # tblMonitoringFiles
    db.go_execute(sql_sqlite_monitoring["delete_table_monitoring_report_files"])
    db.go_execute(sql_sqlite_monitoring["create_table_monitoring_report_files"])
    # tblMonitoringMaterialsReports
    db.go_execute(sql_sqlite_monitoring["delete_table_monitoring_reports"])
    db.go_execute(sql_sqlite_monitoring["create_table_monitoring_reports"])
    db.go_execute(sql_sqlite_monitoring["create_index_monitoring_reports"])
    # tblHistoryPriceMaterials
    db.go_execute(sql_sqlite_materials["delete_table_history_price_materials"])
    db.go_execute(sql_sqlite_materials["create_table_history_price_materials"])
    db.go_execute(sql_sqlite_materials["create_index_history_price_materials"])
    # tblPivotIndexMaterials
    db.go_execute(sql_sqlite_materials["delete_table_pivot_index_materials"])
    db.go_execute(sql_sqlite_materials["create_table_pivot_index_materials"])
    # tblExpandedMaterial
    db.go_execute(sql_sqlite_materials["delete_table_expanded_material"])
    db.go_execute(sql_sqlite_materials["create_table_expanded_material"])
    db.go_execute(sql_sqlite_materials["create_index_expanded_material"])
    # tblMonitoringHistoryPrices
    db.go_execute(sql_sqlite_monitoring["delete_table_monitoring_history_prices"])
    db.go_execute(sql_sqlite_monitoring["create_table_monitoring_history_prices"])
    db.go_execute(sql_sqlite_monitoring["create_index_monitoring_history_prices"])
    # tblPivotMonitoringIndex
    db.go_execute(sql_sqlite_monitoring["delete_table_pivot_monitoring_index"])
    db.go_execute(sql_sqlite_monitoring["create_table_pivot_monitoring_index"])

    return 0



def _create_tables_indexes(db_file: str) -> int:
    """
    Создает таблицы:
        Справочников tblDirectories
        Периодов tblPeriods
    """
    # создает инфраструктуру
    with SQLiteDB(db_file) as db:
        _create_periods_environment(db)
        _create_directory_environment(db)
        _create_monitoring_environment(db)
    return 0


def _fill_directories(db_file: str) -> int:
    """
    Заполняет таблицу tblDirectories
    (directory, name, description, parent_id)
    """
    with SQLiteDB(db_file) as db:
        directories = [
            ("owners", "TON", TON_ORIGIN, None),
            ("owners", "monitoring", MONITORING_ORIGIN, None),
            ("owners", "equipment", EQUIPMENT_ORIGIN, None),
            ("owners", "PNWC", PNWC_ORIGIN, None),
            ("owners", "POM", POM_ORIGIN, None),
            ("period_types", "supplement", "дополнение", None),
            ("period_types", "index", "индекс", None),
            ("period_types", "test", "тестовый период", None),
        ]
        result = db.go_execute_many(sql_sqlite_directories["insert_item_directory"], directories)
        message = f"вставлено {result.rowcount} записей в таблицу tblDirectories"
        ic(message)
    return 0

def create_support_db(db_file: str) -> int:
    ic("Создаю Supporting_DB.sqlite3. Заполняю справочники.")
    ic("Все данные уничтожаются!")
    _create_tables_indexes(db_file)
    _fill_directories(db_file)
    return 0



if __name__ == "__main__":

    db_name = DB_FILE
    ic(db_name)
    create_support_db(db_name)

    # with SQLiteDB(db_name) as db:
    #     _create_monitoring_environment(db)