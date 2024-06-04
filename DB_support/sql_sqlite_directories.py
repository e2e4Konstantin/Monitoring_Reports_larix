


sql_sqlite_directories = {
    "select_directory_name": """--sql
        SELECT * FROM tblDirectories WHERE directory = ? AND name = ?;
    """,
    #
    "delete_table_items": """--sql
        DROP TABLE IF EXISTS tblDirectories;""",
    "delete_index_items": """--sql
        DROP INDEX IF EXISTS idxDirectories;""",
    # --- Таблица для хранения справочников ---------------------
    #  directory определяет название справочника
    # ['owners', 'period_types'...]
    #  можно задать иерархию объектов справочника заполнив колонку parent_id
    "create_table_items": """--sql
        CREATE TABLE tblDirectories (
                id INTEGER PRIMARY KEY NOT NULL,
                directory   TEXT NOT NULL,  -- название справочника
                name        TEXT NOT NULL,  -- название
                description TEXT NOT NULL,  -- описание
                parent_id   INTEGER REFERENCES tblDirectories (id) DEFAULT NULL,   -- родитель если справочник иерархический
                last_update INTEGER NOT NULL DEFAULT (UNIXEPOCH('now')),
                UNIQUE (directory, name)
        );
    """,
    "create_main_index_directory": """--sql
        CREATE UNIQUE INDEX idxDirectory ON tblDirectories (directory, name);
    """,
    "create_chain_index_directory": """--sql
        CREATE UNIQUE INDEX idxDirectory_parent ON tblDirectories (parent_id);
    """,
    "insert_item_directory": """--sql
        INSERT INTO tblDirectories (directory, name, description, parent_id) VALUES ( ?, ?, ?, ?);
    """,
}

