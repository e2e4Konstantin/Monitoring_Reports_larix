sql_pg_queries = {
    "select_larix_period_by_regexp_title": """--sql
        SELECT id, title
        FROM larix.period
        WHERE
            deleted_on IS NULL
            AND LOWER(title) ~ %(regexp_pattern)s
        LIMIT 1;
    """,
    "select_materials_for_period_by_regexp_title": """--sql
        -- выбрать материалы по заданному периоду regexp_pattern '^\s*Дополнение\s*72\s*$'
        WITH target_period AS (
            SELECT id FROM larix."period" WHERE LOWER(title) ~ %(regexp_pattern)s LIMIT 1
        )
        SELECT
            r.id "material_id",
            p."title" "period",
            tr.title "type" ,
            r.pressmark "code",
            r.title "description",
            uom.title "unit_measure",
            r.netto,
            r.brutto,
            r.price "base_price",
            r.cur_price "actual_price"
            ,
            tc.pressmark "transport_code",
            tc.title "transport_name",
            tc.price "transport_base_price",
            tc.cur_price "transport_current_price"
            ,
            sc.rate "storage_rate",
            sc.title "storage_name",
            sc.cmt "storage_description"
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
            AND r.pressmark LIKE '1.%%'
            AND r.pressmark NOT LIKE '1.0%%'
        ORDER BY r.pressmark_sort
        LIMIT 5
        ;
    """,
    "select_materials_for_period_id": """--sql
        -- выбрать материалы по заданному id периода'
        SELECT
            r.id "material_id",
            p."title" "period",
            tr.title "type" ,
            r.pressmark "code",
            r.title "description",
            uom.title "unit_measure"
        FROM larix.resources r
        JOIN larix.type_resource tr on tr.id = r.type_resource
        JOIN larix.unit_of_measure uom on uom.id=r.unit_of_measure
        JOIN larix.period p on p.id=r.period
        WHERE
            r."period" = %(period_id)s
            AND r.deleted = 0
            AND tr.code  = 'MR'
            AND r.pressmark LIKE '1.%%'
            AND r.pressmark NOT LIKE '1.0%%'
        ORDER BY r.pressmark_sort
        --LIMIT 5
        ;
    """,
    #
    "test_sql": """--sql
        /*
        db.select(sql_pg_queries["test_sql"],  {
                "period_id": 167085727,
                "starts_pressmark": "1.%",
                "not_starts": "^\s*1\.0",
            },
        )
        */
        SELECT *
        FROM larix.resources r
        WHERE
            r."period" = %(period_id)s
            AND r.deleted = 0
            AND r.pressmark LIKE %(starts_pressmark)s
            AND r.pressmark !~ %(not_starts)s
            LIMIT 10;
    """,
    "select_prices_material_for_target_periods": """--sql
        /*
        получить историю цен материала по material_id
        для индексных периодов начиная с даты создания date_start
        */
        WITH target_periods AS (
            SELECT
                p.id AS "period_id",
                TRIM(SUBSTRING(p.title, 1, 4))::int AS "index_number",
                p.date_start "start_date",
                p.title "period_name"
            FROM larix."period" p
            WHERE
                p.deleted_on IS NULL
                AND p.is_infl_rate = 1
                AND p.period_type = 1
                AND date_start >= %(start_date)s ::date --
                AND LOWER(p.title) ~ '^\s*\d+\s*индекс/дополнение\s*\d+\s*\(.+\)\s*$'
            ORDER BY p.date_start ASC
        )
        SELECT
            r.price "base_price",
            r.cur_price "current_price",
            TRIM(SUBSTRING(tp."period_name", 1, 4))::int AS "index_number"
        FROM larix.resources r
        JOIN target_periods tp ON tp.period_id = r."period"
        WHERE
            id = %(material_id)s -- 27054534
        ORDER BY r.pressmark_sort
        ;
    """,
    #
    "old_select_prices_all_materials_for_target_periods": """--sql
        /*
        получить историю цен ВСЕХ материалов
        для индексных периодов начиная с даты создания date_start
        */
        WITH target_periods AS (
            SELECT
                p.id AS "period_id",
                TRIM(SUBSTRING(p.title, 1, 4))::int AS "index_number",
                p.date_start "start_date",
                p.title "period_name"
            FROM larix."period" p
            WHERE
                p.deleted_on IS NULL
                AND p.is_infl_rate = 1
                AND p.period_type = 1
                AND date_start >= %(start_date)s ::date --'2024-01-01'
                AND LOWER(p.title) ~ '^\s*\d+\s*индекс/дополнение\s*\d+\s*\(.+\)\s*$'
            ORDER BY p.date_start ASC
        )
        SELECT
            r.pressmark "code",
            r.price ::float "base_price",
            r.cur_price::float "current_price",
            TRIM(SUBSTRING(tp."period_name", 1, 4))::int AS "index_number",
            r.netto ::float "net_weight",
            r.brutto ::float "gross_weight",
            --
            tc.pressmark "transport_code",
		    tc.title "transport_name",
		    tc.price ::float "transport_base_price",
		    tc.cur_price ::float "transport_current_price",
		    --
		    sc.rate ::float "storage_rate",
		    sc.title "storage_name",
		    sc.cmt "storage_description",
            r."period" "larix_period_id"
            -- r.pressmark_sort "digit_code"
        FROM larix.resources r
        JOIN target_periods tp ON tp.period_id = r."period"
        --
        JOIN larix.transport_cost tc ON tc.id = r.transport_cost AND tc."period" = r.period
		JOIN larix.storage_cost sc ON sc.id = r.storage_cost AND sc."period" = r.period
        WHERE
            --id IN (27054238,27054240,27054242,27054244,27054246) AND
            r.deleted = 0
            AND r.pressmark LIKE '1.%%'
            AND r.pressmark NOT LIKE '1.0%%'--
        ORDER BY r.pressmark_sort, tp.start_date ASC
        --LIMIT 35
        ;
    """,
    "select_prices_all_materials_for_start_date_periods": """--sql
        WITH target_periods AS (
            SELECT
                p.id AS "period_id",
                p.date_start "start_date",
                p.title "period_name"
            FROM larix."period" p
            WHERE
                p.deleted_on IS NULL
                AND date_start >= %(start_date)s ::date --'2024-01-01'
                AND p.title ~ '^\s*[^ЕТФКТВНХ].+'
			    AND (LOWER(p.title) ~ '^\s*\d+\s*индекс\/дополнение\s*\d+\s*\(.+\)\s*$'
			    	OR LOWER(p.title) ~ '^\s*индекс\s*.*\d{4}\/дополнение\s*\d+')
        )
        SELECT
            r.pressmark "code",
            r.price ::float "base_price",
            r.cur_price::float "current_price",
            r.netto ::float "net_weight",
            r.brutto ::float "gross_weight",
            --
            tc.pressmark "transport_code",
		    tc.title "transport_name",
		    tc.price ::float "transport_base_price",
		    tc.cur_price ::float "transport_current_price",
		    --
		    sc.rate ::float "storage_rate",
		    sc.title "storage_name",
		    sc.cmt "storage_description",
            r."period" "larix_period_id",
            tp.period_name "period_name"
        FROM larix.resources r
        JOIN target_periods tp ON tp.period_id = r."period"
        --
        JOIN larix.transport_cost tc ON tc.id = r.transport_cost AND tc."period" = r.period
		JOIN larix.storage_cost sc ON sc.id = r.storage_cost AND sc."period" = r.period
        WHERE
            r.deleted = 0
            AND r.pressmark LIKE '1.%%'
            AND r.pressmark NOT LIKE '1.0%%'--
        ORDER BY r.pressmark_sort, tp.start_date ASC
        LIMIT 30
        ; 
    """,
    # 
    "select_monitoring_min_prices_for_periods_starting_date": """--sql
        /* Мониторинг цен ресурсов larix.resource_price_list
        *  получает минимальные цены для периодов начиная c даты '2024-01-01'
        */
        WITH
            target_periods AS (
                SELECT
                    p.id AS "period_id",
                    p.title,
                    --
        --			TRIM(SUBSTRING(p.title, 11, 13))::varchar(15) AS "period_name",
                    TRIM((regexp_match(LOWER(p.title), '^\s*мониторинг\s*(.*)\s\('))[1])::varchar AS period_name,
                    TRIM((regexp_match(LOWER(p.title), '^\s*мониторинг\s*.+\(\s*(\d+)\s*'))[1])::varchar AS index_num,
                    p.date_start "start_date"
                FROM larix."period" p
                WHERE
                    deleted_on IS NULL AND period_type = 1 AND date_start >= %(start_date)s ::date
        --			AND title ~ '^\s*[^ЕTФКТВНХ].+'
                    AND p.title ~* '^\s*мониторинг\s*(.*)\s\((\d+)\s+сборник\/дополнение\s+(\d+).*\)\s*$'
                ORDER BY created_on DESC
            )
        SELECT * FROM (
            SELECT
                r.pressmark AS code,
                --r.pressmark_sort AS digit_code,
                --
                tp.period_name,
                tp.index_num AS index_number,
                per.title AS period_title,
                --
                m.resources AS resource_id,
                m.is_delivery_incl AS transport_included_in_price,
                m.price_and_delivery::float AS price,
                min(m.price_and_delivery) OVER (PARTITION BY r.id, per.id)::float AS min_price,
                ROW_NUMBER() OVER (PARTITION BY r.id, per.id, m.price_and_delivery ORDER BY m.id DESC) AS row_num,
                a.agent_name
            --  , m.created_on, m.producer
            FROM larix.resource_price_list m
            JOIN larix."period" per ON per."id" = m."period" AND per.deleted_on IS NULL
            JOIN larix.resources r ON r.id = m.resources AND r."period" = m."period"
            JOIN larix.agent a ON a.id = m.agent AND a."period" = m."period"
            JOIN target_periods tp ON tp.period_id = m."period"
            WHERE
                m.deleted_on IS NULL
                --and m.is_delivery_incl = 1
                --AND r.pressmark IN ( '1.17-1-71', '1.17-2-14')
                --AND m.PERIOD IN (167461475, 167319938, 167177895)
            ORDER BY r.pressmark_sort
        ) AS monitoring_prices
        WHERE
            monitoring_prices.price = monitoring_prices.min_price
            AND monitoring_prices.row_num = 1
        --LIMIT 20
        ;
    """,
}