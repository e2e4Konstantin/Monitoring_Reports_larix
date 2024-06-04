SELECT gr.*
FROM larix.group_resource AS gr
JOIN (
    SELECT (SELECT p.id FROM larix.period p WHERE p.title = 'Дополнение 68') AS id
) vars ON gr.period = vars.id
WHERE gr.deleted = 0 AND gr.pressmark LIKE '1.%'
ORDER BY gr.pressmark_sort
LIMIT 10;

WITH period_ids AS (
    SELECT (SELECT p.id FROM larix.period p WHERE p.title = 'Дополнение 67') AS id_67,
           (SELECT p.id FROM larix.period p WHERE p.title = 'Дополнение 68') AS id_68
)
SELECT gr.*
FROM larix.group_resource AS gr
JOIN period_ids ON gr.period IN (period_ids.id_68, period_ids.id_67)
WHERE gr.deleted = 0 AND gr.pressmark LIKE '1.%'
ORDER BY gr.pressmark_sort
LIMIT 10;

SELECT
	id,
	date_start,
	period_type,
	title,
	is_infl_rate,
	cmt,
	parent_id,
	previous_id,
	base_type_code
FROM larix.period
WHERE deleted_on IS NULL AND period_type = 1 AND date_start > '2024'
ORDER BY created_on DESC;

CREATE TABLE tblPeriods (
        id                  INTEGER PRIMARY KEY NOT NULL,
        parent_id           INTEGER REFERENCES tblPeriods (id), -- родительский период/только для индексов
        chain_id            INTEGER REFERENCES tblPeriods (id), -- следующий период
        name                TEXT NOT NULL, -- название
        supplement_number   INTEGER NOT NULL, -- номер дополнения
        index_number        INTEGER NOT NULL, -- номер индекса
        start_date          TEXT COLLATE NOCASE NOT NULL CHECK(DATE(start_date, '+0 days') == start_date),
        comment             TEXT, -- описание
        --
        owner_id            INTEGER NOT NULL, -- id владельца (TSN, Equipment, Monitoring)
        period_type_id      INTEGER NOT NULL, -- id типа периода (Supplement, Index)
        database_id         INTEGER, -- id main db (Postgres Normative)
        last_update         INTEGER NOT NULL DEFAULT (UNIXEPOCH('now')),

        FOREIGN KEY (owner_id) REFERENCES origins (id),
        FOREIGN KEY (period_type_id) REFERENCES items (id),

        UNIQUE (owner_id, period_type_id, supplement_number, index_number)
    );


   SELECT
            id,
            date_start,
            period_type,
            title,
            is_infl_rate,
            cmt,
            parent_id,
            previous_id,
            base_type_code
        FROM larix.period
        WHERE
            deleted_on IS NULL
            AND period_type = 1
            AND date_start >= '2020-01-01'::date
            AND title ~ '^\s*[^ЕTФКТВНХ].+'
        ORDER BY created_on DESC



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
    AND
    period_type_id = (SELECT id FROM period_type_row)
    ;

SELECT
    periods.id AS [id],
    owners.description AS [owner],
    types.description AS [type],
    periods.name AS [period_name],
    periods.supplement_number AS [supplement],
    periods.index_number AS [index],
    periods.parent_id AS [parent_id],
    (SELECT previous.id FROM tblPeriods AS previous WHERE previous.id = periods.previous_id) AS [previous_id],
    periods.comment AS [comment]
FROM tblPeriods AS periods
JOIN tblDirectories AS owners ON owners.id = periods.owner_id
JOIN tblDirectories AS types ON types.id = periods.period_type_id
ORDER BY
    periods.owner_id ASC,
    periods.supplement_number DESC,
    periods.index_number DESC;

UPDATE periods
SET previous_id = previous_period.id
FROM tblPeriods AS periods
JOIN tblPeriods AS previous_period
    ON previous_period.supplement_number = periods.supplement_number - 1;
