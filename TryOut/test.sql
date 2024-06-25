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

SELECT * FROM larix."period" WHERE title ~'^\s*Дополнение\s*72\s*$';

SELECT
	p.title "period",
	tr.title "type" ,
	--tr.code,
	r.pressmark,
	r.title,
	uom.title "uom",
	r.netto,
	r.brutto,
	r.price "базовая стоимость",
	r.cur_price "текущая стоимость",
	r.*
FROM larix.resources r
JOIN larix.type_resource tr on tr.id = r.type_resource
JOIN larix.unit_of_measure uom on uom.id=r.unit_of_measure
JOIN larix.period p on p.id=r.period
WHERE
	r."period" = (SELECT id FROM larix."period" WHERE title ~'^\s*Дополнение\s*72\s*$' LIMIT 1)
	AND r.deleted = 0
	AND tr.code  = 'MR'
	AND r.pressmark ~ '^\s*1\.'
	AND r.pressmark !~ '^\s*1\.0'
ORDER BY r.pressmark_sort
--LIMIT 30
;

WITH target_period AS (
    SELECT id FROM larix."period" WHERE title ~'^\s*Дополнение\s*72\s*$' LIMIT 1
)
SELECT
	p.title "period",
	tr.title "type" ,
	r.pressmark "code",
	r.title "description",
	uom.title "unit_of_measuare",
	r.netto,
	r.brutto,
	r.price "base_price",
	r.cur_price "curent_price"
	,
	tc.pressmark "transport_code",
	tc.title "transport_name",
	tc.price "transport_base_price",
	tc.cur_price "transport_current_price"
	,
	sc.title "storage_name",
	sc.rate "storage_rate"
FROM larix.resources r
JOIN larix.type_resource tr on tr.id = r.type_resource
JOIN larix.unit_of_measure uom on uom.id=r.unit_of_measure
JOIN larix.transport_cost tc ON tc.id = r.transport_cost AND tc."period" = (SELECT id FROM target_period)
JOIN larix.storage_cost sc ON sc.id = r.storage_cost AND sc."period" = (SELECT id FROM target_period)
JOIN larix.period p on p.id=r.period
WHERE
	r."period" = (SELECT id FROM target_period)
	AND r.deleted = 0
	AND tr.code  = 'MR'
	AND r.pressmark ~ '^\s*1\.'
	AND r.pressmark !~ '^\s*1\.0'
ORDER BY r.pressmark_sort
--LIMIT 50
;
SELECT * FROM (
WITH
	target_periods AS (
		SELECT
			p.id AS "period_id",
			p.title,
			--
--			TRIM(SUBSTRING(p.title, 11, 13))::varchar(15) AS "period_name",
			TRIM((regexp_match(LOWER(p.title), '^\s*мониторинг\s*(.*)\s\('))[1])::varchar AS period_name,
			p.date_start "start_date"
		FROM larix."period" p
		WHERE
			deleted_on IS NULL AND period_type = 1 AND date_start >= '2024-01-01'::date
			AND title ~ '^\s*[^ЕTФКТВНХ].+'
			AND p.title ~* '^\s*мониторинг\s*(.*)\s\((\d+)\s+сборник\/дополнение\s+(\d+).*\)\s*$'
		ORDER BY created_on DESC
	)
SELECT
	m.id,
	m.resources, m."period",
	r.pressmark,
	pl.title,  pl.period_name,
	m.is_delivery_incl,
	m.price_and_delivery,
	a.agent_name,
	min(m.price_and_delivery) OVER (PARTITION BY r.pressmark,  m.period) AS min_price
--	m.*
FROM larix.resource_price_list m
JOIN larix."period" per ON per."id" = m."period" AND per.deleted_on IS NULL
JOIN larix.resources r ON r.id = m.resources AND r."period" = m."period"
JOIN larix.agent a ON a.id = m.agent AND a."period" = m."period"
JOIN target_periods pl ON pl.period_id = m."period"
WHERE
--	r.pressmark IN ('1.1-1-4', '1.1-1-5', '1.1-1-6') AND
	m.deleted_on IS NULL
--	AND m.PERIOD IN (166991596, 167319938)
--LIMIT 10
) AS history_price
WHERE history_price.price_and_delivery = history_price.min_price
;

SELECT
    p.id,
    p.date_start,
    p.period_type,
    p.title,
    p.is_infl_rate,
    p.cmt,
    p.parent_id,
    p.previous_id,
    p.base_type_code
FROM larix.period p
WHERE
    p.deleted_on IS NULL
    AND p.date_start >= '2020-01-01'::date
    AND p.title ~ '^\s*[^ЕТФКТВНХ].+'
    AND (LOWER(p.title) ~ '^\s*\d+\s*индекс\/дополнение\s*\d+\s*\(.+\)\s*$'
    OR LOWER(p.title) ~ '^\s*индекс\s*.*\d{4}\/дополнение\s*\d+')
ORDER BY p.created_on DESC;
