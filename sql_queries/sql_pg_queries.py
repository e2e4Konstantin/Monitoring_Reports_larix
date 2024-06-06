sql_pg_queries = {
    "select_materials_for_period": """--sql
        -- выбрать материалы по заданному периоду regexp_pattern '^\s*Дополнение\s*72\s*$'
        WITH target_period AS (
            SELECT id FROM larix."period" WHERE title ~ %(regexp_pattern)s LIMIT 1
        )
        SELECT
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
        --LIMIT 50
        ;
    """,
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
}