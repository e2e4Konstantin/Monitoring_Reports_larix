sql_materials = {
    "select_materials_by_period": """--sql
        -- выбрать материалы по периоду
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
}

