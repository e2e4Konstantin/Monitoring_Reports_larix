"select_ton_index_by_number": """--sql
        WITH
            owner_row AS (
                SELECT id FROM  tblDirectories WHERE directory = 'owners' AND name = 'TON'
            ),
            period_type_row AS (
                SELECT id FROM  tblDirectories WHERE directory = 'period_types'  AND name = 'index'
            )
        SELECT *
        FROM tblPeriods
        WHERE
            owner_id = (SELECT id FROM owner_row)
            AND period_type_id = (SELECT id FROM period_type_row)
            AND index_number = :index_number
        ;