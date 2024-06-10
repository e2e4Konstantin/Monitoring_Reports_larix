sql_duck_db = {
    "insert_row_material_prices": """--sql
        INSERT INTO tblMaterialPrices (
            code, base_price, current_price, index_number
        )
        VALUES ( ?, ?, ?, ? );
    """,
    # "insert_row_material_prices": """--sql
    #     INSERT INTO tblMaterialPrices (
    #         code, base_price, current_price, index_number
    #     )
    #     VALUES ( $code, $base_price, $current_price, $index_number );
    # """,
    "delete_table_material_prices": """DROP TABLE IF EXISTS tblMaterialPrices;""",
    "delete_all_data_material_prices": """DELETE FROM tblMaterialPrices;""",
    "create_table_material_prices": """--sql
        CREATE TABLE tblMaterialPrices (
            -- таблица для хранения истории цен на Материалы.
            --id INTEGER PRIMARY KEY,
            --
            code VARCHAR,
            base_price REAL,
            current_price REAL,
            index_number INTEGER
        );
    """,
    "create_index_material_prices": """--sql
        CREATE INDEX idxMaterialPrices ON tblMaterialPrices (code);
    """,
    "select_all_prices": """SELECT * FROM tblMaterialPrices;""",
}


