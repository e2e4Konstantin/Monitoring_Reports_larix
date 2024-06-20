
# ---> Периоды -----------------------------------------------------------------------
sql_sqlite_periods = {
    "update_previous_id_by_id": """--sql
        UPDATE tblPeriods
        SET previous_id = :previous_id, parent_id = :parent_id
        WHERE id=:id;
        """,
    #
    "delete_table_periods": """--sql
        DROP TABLE IF EXISTS tblPeriods;
    """,
    "delete_index_periods": """--sql
        DROP INDEX IF EXISTS idxPeriods;
    """,
    "delete_all_data_periods": """DELETE FROM tblPeriods;
    """,
    "delete_period_by_id": """DELETE FROM tblPeriods WHERE id=:period_id;
    """,
    "delete_view_periods": """DROP VIEW IF EXISTS viewPeriods;""",
    "create_table_periods": """--sql
    /*
    Таблица для хранения периодов.
    Владелец/источник по которому ведется период: ТСН, Оборудование, Мониторинг...
    Категория периода: Дополнение, Индекс...
    Периоды ТСН это весь ТСН кроме 13 главы. 13 глава (оборудование) ведется по своим периодам.
    Периоды мониторинга несут смысловую нагрузку индекса (цены).
    Периоды мониторинга ни как не связаны с периодами ТСН, хотя по смыслу привязаны к индексу.
    parent_id, previous_id, name, supplement_number, index_number, start_date, comment, owner_id, period_type_id, database_id
    */

    CREATE TABLE tblPeriods (
        id                  INTEGER PRIMARY KEY NOT NULL,
        parent_id           INTEGER REFERENCES tblPeriods (id), -- родительский период/только для индексов
        previous_id         INTEGER REFERENCES tblPeriods (id), -- предыдущий период
        name                TEXT NOT NULL,      -- название
        supplement_number   INTEGER NOT NULL,   -- номер дополнения
        index_number        INTEGER NOT NULL,   -- номер индекса
        start_date          TEXT COLLATE NOCASE NOT NULL CHECK(DATE(start_date, '+0 days') == start_date),
        comment             TEXT, -- описание
        --
        owner_id            INTEGER NOT NULL, -- id владельца (TSN, Equipment, Monitoring)
        period_type_id      INTEGER NOT NULL, -- id типа периода (Supplement, Index)
        database_id         INTEGER, -- id периода в larix(Postgres Normative)
        last_update         INTEGER NOT NULL DEFAULT (UNIXEPOCH('now')),
        --
        FOREIGN KEY (owner_id) REFERENCES tblDirectories (id),
        FOREIGN KEY (period_type_id) REFERENCES tblDirectories (id),
        --
        UNIQUE (owner_id, period_type_id, supplement_number, index_number, start_date)
    );
    """,
    "create_index_periods": """--sql
        CREATE INDEX idxPeriods ON tblPeriods (
            parent_id, previous_id, owner_id, period_type_id, supplement_number, index_number
        );
    """,
    "create_view_periods": """--sql
        CREATE VIEW viewPeriods AS
            SELECT
                periods.id AS [id],
                owners.description AS [owner],
                types.description AS [type],
                periods.name AS [name],
                periods.supplement_number AS [supplement],
                periods.index_number AS [index],
                (SELECT previous.name FROM tblPeriods AS previous WHERE previous.id = periods.parent_id) AS [parent],
                (SELECT previous.name FROM tblPeriods AS previous WHERE previous.id = periods.previous_id) AS [previous],
                periods.comment AS [comment],
                strftime('%Y',  periods.start_date) AS [year],
                strftime('%m', periods.start_date) AS [month],
                periods.start_date
            FROM tblPeriods AS periods
            JOIN tblDirectories AS owners ON owners.id = periods.owner_id
            JOIN tblDirectories AS types ON types.id = periods.period_type_id
            ORDER BY
                periods.owner_id ASC,
                periods.supplement_number DESC,
                periods.index_number DESC
                ;
    """,
    "insert_period": """--sql
        -- parent_id, previous_id, name, supplement_number, index_number, start_date,
        -- comment, owner_id, period_type_id, database_id
        INSERT INTO tblPeriods
            (
                parent_id,
                previous_id,
                name,
                supplement_number,
                index_number,
                start_date,
                comment,
                owner_id,
                period_type_id,
                database_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ;
    """,
    "select_ton_supplements": """--sql
        WITH
            owner_row AS (
                SELECT id FROM tblDirectories WHERE directory='owners' AND name='TON'
            ),
            period_type_row AS (
                SELECT id FROM tblDirectories WHERE directory='period_types' AND name='supplement'
            )
        SELECT *
        FROM tblPeriods
        WHERE
            owner_id = (SELECT id FROM owner_row)
            AND period_type_id = (SELECT id FROM period_type_row)
        --ORDER BY supplement_number ASC
        ;
    """,
    "select_ton_indexes": """--sql
        WITH
            owner_row AS (
                SELECT id FROM tblDirectories WHERE directory='owners' AND name='TON'
            ),
            period_type_row AS (
                SELECT id FROM tblDirectories WHERE directory='period_types' AND name='index'
            )
        SELECT *
        FROM tblPeriods
        WHERE
            owner_id = (SELECT id FROM owner_row)
            AND period_type_id = (SELECT id FROM period_type_row)
        --ORDER BY supplement_number DESC, index_number DESC
        ;
    """,
    "select_monitoring": """--sql
        WITH
            owner_row AS (
                SELECT id FROM tblDirectories WHERE directory='owners' AND name='monitoring'
            ),
            period_type_row AS (
                SELECT id FROM tblDirectories WHERE directory='period_types' AND name='index'
            )
        SELECT *
        FROM tblPeriods
        WHERE
            owner_id = (SELECT id FROM owner_row)
            AND period_type_id = (SELECT id FROM period_type_row)
        ORDER BY start_date DESC, supplement_number DESC, index_number DESC
        ;
    """,
    "select_ton_supplement_by_supplement_number": """--sql
        WITH
            owner_row AS (
                SELECT id FROM tblDirectories WHERE directory='owners' AND name='TON'
            ),
            period_type_row AS (
                SELECT id FROM tblDirectories WHERE directory='period_types' AND name='supplement'
            )
        SELECT *
        FROM tblPeriods
        WHERE
            owner_id = (SELECT id FROM owner_row)
            AND period_type_id = (SELECT id FROM period_type_row)
            AND supplement_number = :supplement_number
        ;
    """,
    "select_monitoring_by_comment": """--sql
        WITH
            owner_row AS (
                SELECT id FROM  tblDirectories WHERE directory = 'owners' AND name = 'monitoring'
            ),
            period_type_row AS (
                SELECT id FROM  tblDirectories WHERE directory = 'period_types'  AND name = 'index'
            )
        SELECT *
        FROM tblPeriods
        WHERE
            owner_id = (SELECT id FROM owner_row)
            AND period_type_id = (SELECT id FROM period_type_row)
            AND TRIM(LOWER(comment)) = TRIM(LOWER(:monitoring_comment))
        ;
    """,
    "select_by_id": """--sql
        SELECT * FROM tblPeriods WHERE id = :period_id
        ;
    """,
    "select_ton_supplement_by_number": """--sql
        WITH
            owner_row AS (
                SELECT id FROM  tblDirectories WHERE directory = 'owners' AND name = 'TON'
            ),
            period_type_row AS (
                SELECT id FROM  tblDirectories WHERE directory = 'period_types'  AND name = 'supplement'
            )
        SELECT *
        FROM tblPeriods
        WHERE
            owner_id = (SELECT id FROM owner_row)
            AND period_type_id = (SELECT id FROM period_type_row)
            AND supplement_number = :supplement_number
        ;
    """,
    "select_by_larix_id": """--sql
        SELECT * FROM tblPeriods WHERE database_id = :larix_period_id;
    """,
}
