sql_materials = {
    "select_materials_by_period": """--sql
        -- выбрать материалы по периоду :period_id
        SELECT
            period.title AS period_title,
            resource.pressmark AS material_code,
            resource.title AS material_title,
            unit_measure.title AS unit_measure,
            type_resource.title AS type_resource_title
        FROM larix.resources resource
        JOIN larix.period period ON period.id = resource.period
        JOIN larix.type_resource type_resource ON type_resource.id = resource.type_resource
        JOIN larix.unit_of_measure unit_measure ON unit_measure.id = resource.unit_of_measure
        WHERE
            resource.deleted = 0
            AND resource.pressmark ~ '^\s*1\.'
            AND resource.pressmark !~ '^\s*1\0.'
            AND resource.period = :period_id
        ORDER BY resource.pressmark_sort
        ;
    """,
    "": """--sql
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
                AND date_start >= '2024-01-01'::date
                AND LOWER(p.title) ~ '^\s*\d+\s*индекс/дополнение\s*\d+\s*\(.+\)\s*$'
            ORDER BY p.date_start ASC
        )
        SELECT
            r.pressmark "code",
        --    r.title "description",
            r.price "base_price",
            r.cur_price "current_price",
            TRIM(SUBSTRING(p.title, 1, 4))::int AS "index_number"
        --    ,
        --    p.title
        FROM larix.resources r
        JOIN larix."period" p on p.id=r."period"
        WHERE
            id = 27054534
            AND r."period" IN (SELECT period_id FROM target_periods)
            AND r.deleted = 0
            AND r.pressmark LIKE '1.%'
            AND r.pressmark NOT LIKE '1.0%'
        ORDER BY r.pressmark_sort
        ;
    """,
}

