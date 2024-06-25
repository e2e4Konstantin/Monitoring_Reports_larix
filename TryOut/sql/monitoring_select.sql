SELECT
    p.id AS "period_id",
    p.title,
    p.date_start "start_date"
FROM larix."period" p
WHERE
    deleted_on IS NULL  
    AND date_start >= '2024-01-01' ::date -- %(start_date)s 
    AND (p.title ~* '^\s*мониторинг\s*(.*)\s\((\d+)\s+сборник\/дополнение\s+(\d+).*\)\s*$'
    	OR p.title ~* '^\s*мониторинг\s*(.*)\s\(\s*дополнение\s*(\s*\d*\s*)\)\s*$'				
    )
ORDER BY created_on desc
; 

------------------------------------------------------------------------------------------------------

                

/*
 larix.resource_price_list
 По данным мониторинга:
 получает минимальные цены для периодов начиная c даты '2024-01-01'
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
                    deleted_on IS NULL AND period_type = 1 AND date_start >= '2024-01-01' ::date -- %(start_date)s
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
                per.id AS period_id,
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