
sql_sqlite_queries = {
    "select_all_raw_table": """--sql
        SELECT  rowid, * FROM tblRawData;
    """,
    "select_count_raw_table": """--sql
        SELECT COUNT() AS row_count FROM tblRawData;
    """,
    #
    "delete_raw_table": """--sql
        DROP TABLE IF EXISTS tblRawData;
    """,
    "create_raw_table_code_index": """--sql
        CREATE INDEX idxRawData ON tblRawData (code );
    """,
    "add_digit_code_column_raw_table": """--sql
        ALTER TABLE tblRawData ADD digit_code INTEGER;
    """,
    "update_digit_code_raw_table": """--sql
        UPDATE tblRawData SET digit_code = :digit_code where rowid = :id;
    """,
}

