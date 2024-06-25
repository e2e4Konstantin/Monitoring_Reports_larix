sql_pg_export = {
    "get_all_periods": """--sql
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
            -- AND period_type = 1 -- открытый 0 / закрытый 1  (не актуальный)
            AND date_start >= '2020-01-01'::date
            AND title ~ '^\s*[^ЕTФКТВНХ].+'
        ORDER BY created_on DESC
        ;
    """,
    #
    "select_period_id_by_title_regexp": """--sql
        -- '^\s*Дополнение\s*72\s*$'
        SELECT p.id, p.title
        FROM larix.period p
        WHERE
            p.deleted_on IS NULL
            AND p.period_type = 1
            AND p.is_infl_rate = 0
            AND p.title ~ :title_regexp
        LIMIT 1;
    """,
    #
    "test_sql": """--sql
        SELECT *
        FROM larix.period
        WHERE
            deleted_on IS NULL
            AND period_type = 1
            AND is_infl_rate = 1
            AND "id" IN %(period_ids)s
        ;
    """,
}