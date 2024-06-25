sql_sqlite_monitoring = {
    #
    "delete_table_monitoring_history_prices": """DROP TABLE IF EXISTS tblMonitoringHistoryPrices;""",
    "delete_index_monitoring_history_prices": """DROP INDEX IF EXISTS tblMonitoringHistoryPrices;""",
    "delete_all_data_monitoring_history_prices": """DELETE FROM tblMonitoringHistoryPrices;""",
    "create_table_monitoring_history_prices": """--sql
        CREATE TABLE tblMonitoringHistoryPrices (
            -- таблица для хранения исторических цен мониторинга
            id INTEGER PRIMARY KEY NOT NULL,
            code TEXT,
            digit_code INTEGER,
            period_name TEXT,
            index_number INTEGER,
            period_title TEXT,
            resource_id INTEGER,
            --
            transport_included_in_price INTEGER,
            price REAL,
            min_price REAL,
            agent_name TEXT
        );
    """,
    "create_index_monitoring_history_prices": """--sql
        CREATE INDEX idxMonitoringHistoryPrices ON tblMonitoringHistoryPrices (
            code, digit_code, period_name, index_number
        );
    """,
    "insert_row_monitoring_history_prices": """--sql
        INSERT INTO tblMonitoringHistoryPrices (
            code, digit_code, period_name, index_number, period_title, resource_id,
            transport_included_in_price, price, min_price, agent_name
        )
        VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """,
    "select_all_monitoring_history_price": """--sql
        SELECT * FROM tblMonitoringHistoryPrices ORDER BY digit_code;
    """,
    "select_code_monitoring_history_price": """--sql
        SELECT * FROM tblMonitoringHistoryPrices where code = ? ORDER BY index_number;
    """,
    "select_unique_code_monitoring_history_price": """--sql
        SELECT DISTINCT code FROM tblMonitoringHistoryPrices ORDER BY digit_code;
    """,
    "select_unique_index_number_monitoring_history_price": """--sql
        SELECT DISTINCT index_number FROM tblMonitoringHistoryPrices ORDER BY index_number;
    """,
    "select_monitoring_history_price_for_code": """--sql
        SELECT
            code,
            period_name,
            index_number,
            min_price AS price,
            transport_included_in_price AS delivery
        FROM tblMonitoringHistoryPrices
        WHERE code = :code
        ORDER BY index_number DESC;
    """,
    # ------------------------------------------------------------------------
    # Pivot
    "delete_table_pivot_monitoring_index": """DROP TABLE IF EXISTS tblPivotMonitoringIndex;""",
    "create_table_pivot_monitoring_index": """--sql
            CREATE TABLE tblPivotMonitoringIndex (
                id INTEGER PRIMARY KEY NOT NULL,
                code TEXT UNIQUE NOT NULL,
                digit_code INTEGER
            );
        """,
    "insert_column_to_pivot_monitoring_index": """--sql
            ALTER TABLE tblPivotMonitoringIndex ADD COLUMN ? REAL;
        """,
    # ------------------------------------------------------------------------
    # Таблица для хранения отчетов мониторинга собранных из файлов
    # ------------------------------------------------------------------------
    "delete_table_monitoring_reports": """DROP TABLE IF EXISTS tblMonitoringMaterialsReports;""",
    "create_table_monitoring_reports": """--sql
        CREATE TABLE tblMonitoringMaterialsReports
            (
                id              INTEGER PRIMARY KEY NOT NULL,
                period_id       INTEGER NOT NULL,
                file_id         INTEGER NOT NULL,
                --
                code            TEXT NOT NULL,
                supplier_price  REAL NOT NULL DEFAULT 0.0,
                delivery        INTEGER NOT NULL DEFAULT 0,
                description     TEXT,
                digit_code      INTEGER,
                --
                UNIQUE (period_id, code)
            );
        """,
    "create_index_monitoring_reports": """--sql
        CREATE UNIQUE INDEX idxMonitoringMaterialsReports ON tblMonitoringMaterialsReports (
            period_id, code
        );
        """,
    "insert_monitoring_item": """--sql
        INSERT INTO tblMonitoringMaterialsReports (
            period_id, file_id, code, supplier_price, delivery, description, digit_code
        )
        VALUES ( :period_id, :file_id, :code, :supplier_price, :delivery, :description, :digit_code
        );
        """,
    "delete_data_for_period_id": """DELETE FROM tblMonitoringMaterialsReports WHERE period_id=:period_id;
        """,
    "select_monitoring_materials_for_period_id": """--sql
        SELECT *
        FROM tblMonitoringMaterialsReports
        WHERE 
            period_id = :period_id
            --AND code IN ( '1.1-1-8134', '1.1-1-8135', '1.3-2-255', '1.3-2-265', '1.3-2-266')
        ORDER BY digit_code
        --LIMIT 5
        ;
    """,
    # ------------------------------------------------------------------------
    # Файлы отчетов
    # ------------------------------------------------------------------------
    "delete_table_monitoring_report_files": """DROP TABLE IF EXISTS tblMonitoringFiles;""",
    "create_table_monitoring_report_files": """--sql
        CREATE TABLE tblMonitoringFiles
            (
                id              INTEGER PRIMARY KEY NOT NULL,
                period_id       INTEGER NOT NULL,
                --
                report_file     TEXT NOT NULL,
                sheet_name      TEXT NOT NULL,
                period_name     TEXT NOT NULL,

                UNIQUE (period_id)
            );
        """,
    "insert_monitoring_files": """--sql
        INSERT INTO tblMonitoringFiles (
            period_id, report_file, sheet_name, period_name
        )
        VALUES ( :period_id, :report_file, :sheet_name, :period_name);
    """,
    "select_monitoring_files_by_period_id": """--sql
        select * from tblMonitoringFiles where period_id = :period_id;
    """,
    "delete_monitoring_files_by_period_id": """--sql
        DELETE FROM tblMonitoringFiles WHERE period_id = :period_id;
    """,
}


