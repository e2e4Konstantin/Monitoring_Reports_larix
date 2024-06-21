sql_sqlite_materials = {
    # ----------------------------------------------------------------------
    # материалы в развернутом виде (по периодам Дополнения)
    # ----------------------------------------------------------------------
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
            period_id INTEGER DEFAULT NULL,
            --
            product_type TEXT,
            code TEXT,
            digit_code INTEGER,
            description TEXT,
            unit_measure TEXT,
            --
            FOREIGN KEY (period_id) REFERENCES tblPeriods (id)
        );
        """,
    "create_index_expanded_material": """--sql
        CREATE INDEX idxExpandedMaterial ON tblExpandedMaterial (
            code, digit_code
        );
        """,
    "insert_row_expanded_material": """--sql
        INSERT INTO tblExpandedMaterial (
            period_larix_id, period_name, period_id,
            product_type, code, digit_code, description, unit_measure
        )
        VALUES (
            :period_larix_id, :period_name, :period_id,
            :product_type, :code, :digit_code, :description, :unit_measure
    );
    """,
    "select_expanded_material_by_code_period_id": """--sql
        SELECT *
        FROM tblExpandedMaterial
        WHERE
            period_id = :period_id 
            AND code = :code
        ;
        """,
    # ----------------------------------------------------------------------
    # история цен материалов
    # ----------------------------------------------------------------------
    "delete_table_history_price_materials": """DROP TABLE IF EXISTS tblHistoryPriceMaterials;""",
    "delete_index_history_price_materials": """DROP INDEX IF EXISTS idxHistoryPriceMaterials;""",
    "delete_all_data_history_price_materials": """DELETE FROM tblHistoryPriceMaterials;""",
    "create_table_history_price_materials": """--sql
        CREATE TABLE tblHistoryPriceMaterials (
            -- таблица для хранения цен на Материалы для индексных периодов
            id INTEGER PRIMARY KEY NOT NULL,
            index_number INTEGER, -- номер индексного периода
            period_id INTEGER DEFAULT NULL,
            code TEXT,
            digit_code INTEGER,
            base_price REAL,
            current_price REAL,
            inflation_ratio REAL GENERATED ALWAYS AS (
                CASE
                    WHEN base_price = 0 THEN 0
                    ELSE ROUND(current_price / base_price, 2)
                END
            ) VIRTUAL,
            --
            net_weight REAL DEFAULT 0.0,
            gross_weight REAL DEFAULT 0.0,
            --
            transport_code TEXT,
            transport_name TEXT,
            transport_base_price REAL,
            transport_current_price REAL,
            transport_inflation_rate REAL GENERATED ALWAYS AS (
                CASE
                    WHEN transport_base_price = 0 THEN 0
                    ELSE ROUND(transport_current_price / transport_base_price, 2)
                END
            ) VIRTUAL,
            --
            storage_cost_rate  REAL,
            storage_cost_name TEXT,
            storage_cost_description TEXT
        );

    """,
    "create_index_history_price_materials": """--sql
        CREATE INDEX idxHistoryPriceMaterials ON tblHistoryPriceMaterials (
            code, digit_code, index_number
        );
    """,
    "insert_row_history_price_materials": """--sql
        INSERT INTO tblHistoryPriceMaterials (
            index_number, period_id,
            code, digit_code, base_price, current_price,
            net_weight, gross_weight,
            transport_code, transport_name, transport_base_price, transport_current_price,
            storage_cost_rate, storage_cost_name, storage_cost_description
        )
        VALUES (
            :index_number, :period_id,
            :code, :digit_code, :base_price, :current_price,
            :net_weight, :gross_weight,
            :transport_code, :transport_name, :transport_base_price, :transport_current_price,
            :storage_cost_rate, :storage_cost_name, :storage_cost_description
        );
    """,
    "select_all_history_price_materials": """--sql
        SELECT * FROM tblHistoryPriceMaterials ORDER BY digit_code;
    """,
    "select_code_history_price_materials": """--sql
        SELECT * FROM tblHistoryPriceMaterials where code = ? ORDER BY index_number;
    """,
    "select_history_price_materials_period_id_code": """--sql
        SELECT * FROM tblHistoryPriceMaterials 
        WHERE period_id = :period_id AND code = :product_code;
    """,

    "select_unique_code_history_price_materials": """--sql
        SELECT DISTINCT code FROM tblHistoryPriceMaterials ORDER BY digit_code;
    """,
    "select_unique_index_number_history_price_materials": """--sql
        SELECT DISTINCT index_number FROM tblHistoryPriceMaterials ORDER BY index_number;
    """,
    # ----------------------------------------------------------------------
    # Pivot
    # tblPivotIndexMaterials развернутая по номерам индексных периодов таблица tblHistoryPriceMaterials
    "delete_table_pivot_index_materials": """--sql
        DROP TABLE IF EXISTS tblPivotIndexMaterials;
        """,
    "create_table_pivot_index_materials": """--sql
            CREATE TABLE tblPivotIndexMaterials (
                id INTEGER PRIMARY KEY NOT NULL,
                code TEXT UNIQUE NOT NULL,
                digit_code INTEGER
            );
        """,
    "insert_column_to_pivot_index_materials": """--sql
            ALTER TABLE tblPivotIndexMaterials ADD COLUMN "{}" REAL;
        """,
    "create_index_pivot_index_materials": """--sql
        CREATE INDEX tblPivotIndexMaterials ON tblHistoryPriceMaterials (
            code, digit_code
        );
    """,
}


