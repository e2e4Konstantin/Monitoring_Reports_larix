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
        JOIN larix.transport_cost tc ON tc.id = r.transport_cost AND tc."period" = %(period_id)s
        JOIN larix.storage_cost sc ON sc.id = r.storage_cost AND sc."period" = %(period_id)s
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
    "select_prices_all_materials_for_target_periods": """--sql
        /*
        получить историю цен ВСЕХ материалов по material_id
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
            r.price "base_price",
            r.cur_price "current_price",
            TRIM(SUBSTRING(tp."period_name", 1, 4))::int AS "index_number"
        FROM larix.resources r
        JOIN target_periods tp ON tp.period_id = r."period"
        WHERE
            r.deleted = 0
            AND r.pressmark LIKE '1.%%'
            AND r.pressmark NOT LIKE '1.0%%'--
        ORDER BY r.pressmark_sort, tp.start_date ASC
        --LIMIT 30
        ;
    """,
}