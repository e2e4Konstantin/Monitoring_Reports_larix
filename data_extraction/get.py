
def get_materials_with_monitoring(
    db_file: str, history_depth: int
) -> list[Material] | None:
    """Стоимость материалов с данными последнего загруженного мониторинга."""
    table = None
    with dbTolls(db_file) as db:
        # получить id записей материалов с максимальным индексом периода и данными мониторинга
        materials = db.go_select(
            sql_materials_reports["select_records_for_max_index_with_monitoring"]
        )
        table = [
            _materials_constructor(db, material, history_depth)
            for material in materials
        ]
    return table if table else None