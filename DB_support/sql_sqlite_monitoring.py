sql_sqlite_monitoring_history_prices = {
    #
    "delete_table": """DROP TABLE IF EXISTS tblMonitoringHistoryPrices;""",
    "delete_index": """DROP INDEX IF EXISTS tblMonitoringHistoryPrices;""",
    "delete_all_data": """DELETE FROM tblMonitoringHistoryPrices;""",
    "create_table": """--sql
        CREATE TABLE tblMonitoringHistoryPrices (
            -- таблица для хранения цен мониторинга
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
    "create_index": """--sql
        CREATE INDEX idxMonitoringHistoryPrices ON tblMonitoringHistoryPrices (
            code, digit_code, period_name, index_number
        );
    """,
    "insert_row": """--sql
        INSERT INTO tblMonitoringHistoryPrices (
            code, digit_code, period_name, index_number, period_title, resource_id,
            transport_included_in_price, price, min_price, agent_name
        )
        VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """,
    "select_all": """--sql
        SELECT * FROM tblMonitoringHistoryPrices ORDER BY digit_code;
    """,
    "select_code": """--sql
        SELECT * FROM tblMonitoringHistoryPrices where code = ? ORDER BY index_number;
    """,
    "select_unique_code": """--sql
        SELECT DISTINCT code FROM tblMonitoringHistoryPrices ORDER BY digit_code;
    """,
    "select_unique_index_number": """--sql
        SELECT DISTINCT index_number FROM tblMonitoringHistoryPrices ORDER BY index_number;
    """,
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
}


