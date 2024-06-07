sql_sqlite_materials = {
    "insert_row_expanded_material": """--sql
        INSERT INTO tblExpandedMaterial (
            period_larix_id, period_name,
            product_type, code, digit_code, description, unit_measure,
            transport_code, transport_name, transport_base_price, transport_current_price, transport_inflation_rate,
            storage_cost_rate, storage_cost_name, storage_cost_description,
            base_price, current_price, inflation_rate
        )
        VALUES (
            :period_larix_id, :period_name,
            :product_type, :code, :digit_code, :description, :unit_measure,
            :transport_code, :transport_name, :transport_base_price, :transport_current_price, :transport_inflation_rate,
            :storage_cost_rate, :storage_cost_name, :storage_cost_description,
            :base_price, :current_price, :inflation_rate
    );
    """,
    "delete_table_expanded_material": """DROP TABLE IF EXISTS tblExpandedMaterial;""",
    "delete_index_expanded_material": """DROP INDEX IF EXISTS idxExpandedMaterial;""",
    "delete_all_data_expanded_material": """DELETE FROM tblExpandedMaterial;""",
    "create_table_expanded_material": """--sql
        CREATE TABLE tblExpandedMaterial (
            -- таблица для хранения развернутых Материалов для периодов
            -- развернутый: собранный из всех связанных таблиц
            id INTEGER PRIMARY KEY NOT NULL,
            --
            period_larix_id INTEGER,
            period_name TEXT,
            --
            product_type TEXT,
            code TEXT,
            digit_code INTEGER,
            description TEXT,
            unit_measure TEXT,
            --
            transport_code TEXT,
            transport_name TEXT,
            transport_base_price REAL,
            transport_current_price REAL,
            transport_inflation_rate REAL,
            --
            storage_cost_rate REAL,
            storage_cost_name TEXT,
            storage_cost_description TEXT,
            --
            base_price REAL,
            current_price REAL,
            inflation_rate REAL
        );
    """,
    "create_index_expanded_material": """--sql
        CREATE INDEX idxExpandedMaterial ON tblExpandedMaterial (
            code, digit_code
        );
    """,
    #
    "delete_table_history_price_materials": """DROP TABLE IF EXISTS tblHistoryPriceMaterials;""",
    "delete_index_history_price_materials": """DROP INDEX IF EXISTS idxHistoryPriceMaterials;""",
    "delete_all_data_history_price_materials": """DELETE FROM tblHistoryPriceMaterials;""",
    "create_table_history_price_materials": """--sql
        CREATE TABLE tblHistoryPriceMaterials (
            -- таблица для хранения цен на Материалы для индексных периодов
            id INTEGER PRIMARY KEY NOT NULL,
            code TEXT,
            digit_code INTEGER,
            base_price REAL,
            current_price REAL
        );
    """,
    "create_index_history_price_materials": """--sql
        CREATE INDEX idxHistoryPriceMaterials ON tblHistoryPriceMaterials (
            code, digit_code
        );
    """,
}

