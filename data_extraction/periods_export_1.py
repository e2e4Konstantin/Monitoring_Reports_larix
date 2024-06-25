import sqlite3
import re
import pandas as pd
import os
from icecream import ic

#
from config import (
    ais_access,
    DatabaseAccess,
    PostgresDB,
    DB_FILE_PATH,
    RAW_DATA_TABLE_NAME,
    DB_FILE,
    PERIOD_PATTERNS,
    PERIOD_CSV_FILE,
    TON_ORIGIN,
)
from sql_queries import sql_pg_export
from DB_support.sql_sqlite_periods import sql_sqlite_periods
from DB_support.sql_sqlite_directories import sql_sqlite_directories
from DB_support.db_config import SQLiteDB
from common_features import (
    output_message_exit,
    clean_text,
    get_integer,
    parse_date,
    date_to_numbers,
    extract_supplement_number,
    extract_supplement_index_cmt,
    extract_monitoring_supplement_index_cmt,
)


def _export_table_periods_to_csv(csv_file: str, pgr_access: DatabaseAccess):
    """Сохраняет запрос на выборку larix.period в CSV файл."""
    with PostgresDB(pgr_access) as db:
        query = sql_pg_export["get_all_periods"]
        results = db.select(query)
        if results:
            df = pd.DataFrame(results)
            df.columns = results[0].keys()
            df.to_csv(csv_file, mode="w", encoding="utf-8", header=True, index=False)
            return 0
    return 1

def _load_dataframe_to_database_table( df: pd.DataFrame, db_file: str, table_name: str) -> int:
    """Загружает данные из df в таблицу table_name базы данных db_file"""
    with SQLiteDB(db_file) as db:
        df.to_sql(
            table_name, db.connection, if_exists="replace", index=False, chunksize=100, method="multi"
        )
        # dtype=pandas.StringDtype(),
        [result] = db.go_select(f"SELECT COUNT(*) AS count FROM {table_name};")
        count = result["count"]
        message = f"В таблицу {table_name!r} импортировано: {count} записей "
        ic(message)
    return 0


def _load_csv_to_raw_table(csv_path: str, db_path: str, delimiter: str = ";") -> int:
    """Импорт данных из файла CSV в таблицу tblRawData"""
    df = pd.read_csv(csv_path, delimiter=delimiter, index_col=False, dtype=str)
    # df.to_clipboard()
    return _load_dataframe_to_database_table(df, db_path, RAW_DATA_TABLE_NAME)


def _fetch_data_by_pattern(
    db: SQLiteDB,
    table_name: str,
    field_name: str,
    pattern: str
) -> list[sqlite3.Row] | None:
    """Выбрать записи по полю column_name в соответствии с (re) паттерном из таблицы table_name."""
    query = f"SELECT * FROM {table_name} WHERE {field_name} REGEXP ?;"
    lines = db.go_select(query, (pattern,))
    if not lines:
        output_message_exit(
            f"в таблице {table_name!r} не найдено ни одной записи:",
            f"соответствующей шаблону {pattern!r} в поле {field_name!r}",
        )
        return None
    return lines

def _get_directory_id(db: SQLiteDB, directory_name: str, item_name: str) -> int | None:
    """Получает Id элемента справочника  с именем owner_name."""
    if item_name is None:
        return None
    [result] = db.go_select(
        sql_sqlite_directories["select_directory_name"],
        (
            directory_name,
            item_name,
        ),
    )
    if result:
        return result["id"]
    output_message_exit(
        f"в справочнике {directory_name!r} не найдена:",
        f"запись с именем: {item_name!r}.",
    )


def _insert_period(db: SQLiteDB, data) -> int | None:
    """Вставляет новый период в таблицу tblPeriods."""
    result = db.go_execute(sql_sqlite_periods["insert_period"], data)
    if result:
        return result.lastrowid
    return None

def _extract_supplement_data_from_line(
    db: SQLiteDB, line: sqlite3.Row, owner_id: int, period_type_id: int
) -> tuple:
    """Извлекает данные из строки  с периодом дополнение."""
    title = clean_text(line["title"])
    supplement = extract_supplement_number(title)
    date = parse_date(clean_text(line["date_start"]))
    comment = clean_text(line["cmt"])
    basic_id = line["id"]
    parent_id = None
    chain_id = None
    # ic(title, supplement, date)
    #
    name = f"Дополнение {supplement}"
    index_number = 0
    # parent_id, chain_id, name, supplement_number, index_number, start_date,
    # comment, owner_id, period_type_id, database_id
    data = (parent_id, chain_id, name, supplement, index_number, date, comment, owner_id, period_type_id, basic_id)
    return data

def _create_supplement_chain_periods(db_file: str) -> int:
    """Создание последовательности периодов дополнений."""
    with SQLiteDB(db_file) as db:
        periods = db.go_select(sql_sqlite_periods["select_ton_supplements"])
        if not periods:
            return None
        data = {
            period["supplement_number"]: (period["id"], period["supplement_number"])
            for period in periods
        }
        for item in data.keys():
            previous = data.get(item-1, None)
            if previous:
                db.go_select(sql_sqlite_periods["update_previous_id_by_id"],
                                ({"previous_id": previous[0],
                                  "id":data[item][0],
                                  "parent_id": None}))
            else:
                db.go_select(
                    sql_sqlite_periods["update_previous_id_by_id"],
                    ({"previous_id": None, "id": data[item][0], "parent_id": None}),
                )
    return 0


def _create_index_chain_periods(db_file: str) -> int:
    """Создание последовательности индексных периодов."""
    with SQLiteDB(db_file) as db:
        periods = db.go_select(sql_sqlite_periods["select_ton_indexes"])
        if not periods:
            return None
        data = {
            period["index_number"]: (
                period["id"],
                period["index_number"],
                period["supplement_number"],
            )
            for period in periods
        }
        # ic(data)
        for item in data.keys():
            result = db.go_select(
                sql_sqlite_periods["select_ton_supplement_by_supplement_number"],
                (
                    {
                        "supplement_number": data[item][2],
                    }
                ),
            )
            parent_id = result[0]["id"] if result else None
            previous = data.get(item-1, None)
            if previous:
                db.go_select(
                    sql_sqlite_periods["update_previous_id_by_id"],
                    (
                        {
                            "previous_id": previous[0],
                            "id": data[item][0],
                            "parent_id": parent_id,
                        }
                    ),
                )
            else:
                db.go_select(
                    sql_sqlite_periods["update_previous_id_by_id"],
                    (
                        {
                            "previous_id": None,
                            "id": data[item][0],
                            "parent_id": parent_id,
                        }
                    ),
                )
    return 0


def _create_monitoring_chain_periods(db_file) -> int:
    """Создание последовательности периодов мониторинга."""
    with SQLiteDB(db_file) as db:
        periods = db.go_select(sql_sqlite_periods["select_monitoring"])
        if not periods:
            return None
        data = [(period["id"], period["start_date"]) for period in periods]
        for index, item in enumerate(data):
            if index == len(data) - 1:
                next_id = None
            else:
                next_item = data[index + 1]
                next_id = next_item[0]
            db.go_select(
                sql_sqlite_periods["update_previous_id_by_id"],
                (
                    {
                        "previous_id": next_id,
                        "id": item[0],
                        "parent_id": None,
                    }
                ),
            )
        # ic(data)
    return 0




def _ton_supplement_periods_parsing(db: SQLiteDB):
    """Запись периодов ТСН категории 'Дополнение' из tblRawData в таблицу периодов.
    """
    pattern = PERIOD_PATTERNS["supplement"] # "^\s*Дополнение\s+\d+\s*$"
    supplements = _fetch_data_by_pattern(
        db, RAW_DATA_TABLE_NAME, field_name="title", pattern=pattern
    )
    message = f"Прочитано Дополнений: {len(supplements)}"
    ic(message)
    if supplements is None:
        return None
    directory_name = "owners"
    item_name = "TON"
    owner_id = _get_directory_id(db, directory_name, item_name)
    directory_name = "period_types"
    item_name = "supplement"
    period_type_id = _get_directory_id(db, directory_name, item_name)
    ic(owner_id, period_type_id)
    for line in supplements:
        data = _extract_supplement_data_from_line(db, line, owner_id, period_type_id)
        _insert_period(db, data)
    return 0


def _extract_index_data_from_line(
    db: SQLiteDB, line: sqlite3.Row, owner_id: int, period_type_id: int
) -> tuple:
    """Извлекает данные об индексе из строки."""
    title = clean_text(line["title"])
    supplement_number, index_number, cmt = extract_supplement_index_cmt(title)
    date = parse_date(clean_text(line["date_start"]))
    comment = clean_text(cmt)
    basic_id = line["id"]
    parent_id = None
    chain_id = None
    # ic(title, supplement, date)
    name = f"Индекс {index_number}"
    # parent_id, chain_id, name, supplement_number, index_number, start_date,
    # comment, owner_id, period_type_id, database_id
    data = (parent_id, chain_id, name, supplement_number, index_number, date, comment, owner_id, period_type_id, basic_id)
    return data

def _extract_monitoring_data_from_line(
    db: SQLiteDB, line: sqlite3.Row, owner_id: int, period_type_id: int
) -> tuple:
    """Извлекает данные об периоде мониторинга из строки."""
    title = clean_text(line["title"])
    supplement_number, index_number, cmt = extract_monitoring_supplement_index_cmt(title)
    date = parse_date(clean_text(line["date_start"]))
    comment = clean_text(cmt)
    basic_id = line["id"]
    parent_id = None
    chain_id = None
    # ic(title, supplement, date)
    name = f"Мониторинг {cmt} {index_number}/{supplement_number}"
    # parent_id, chain_id, name, supplement_number, index_number, start_date,
    # comment, owner_id, period_type_id, database_id
    data = (
        parent_id,
        chain_id,
        name,
        supplement_number,
        index_number,
        date,
        comment,
        owner_id,
        period_type_id,
        basic_id,
    )
    return data


def _ton_index_periods_parsing(db: SQLiteDB) -> int:
    """Запись периодов ТСН категории 'Индекс' из tblRawData в таблицу периодов."""
    # 209 индекс/дополнение 71 (мониторинг Февраль 2024)
    pattern = PERIOD_PATTERNS["index_old"]
    indexes = _fetch_data_by_pattern(
        db, RAW_DATA_TABLE_NAME, field_name="title", pattern=pattern
    )
    message = f"Прочитано Индексов: {len(indexes)}"
    ic(message)
    if indexes is None:
        return None
    directory_name = "owners"
    item_name = "TON"
    owner_id = _get_directory_id(db, directory_name, item_name)
    directory_name = "period_types"
    item_name = "index"
    period_type_id = _get_directory_id(db, directory_name, item_name)
    # ic(owner_id, period_type_id)
    for line in indexes:
        data = _extract_index_data_from_line(db, line, owner_id, period_type_id)
        _insert_period(db, data)
        # ic(data)
    return 0

def _monitoring_periods_parsing(db: SQLiteDB) -> int:
    """Запись периодов Мониторинга из tblRawData в таблицу периодов."""
    # Мониторинг Октябрь 2023 (205 сборник/дополнение 70)
    pattern = PERIOD_PATTERNS["monitoring"]
    monitors = _fetch_data_by_pattern(
        db, RAW_DATA_TABLE_NAME, field_name="title", pattern=pattern
    )
    message = f"Прочитано периодов: {len(monitors)} мониторинга"
    ic(message)
    if monitors is None:
        return None
    directory_name = "owners"
    item_name = "monitoring"
    owner_id = _get_directory_id(db, directory_name, item_name)
    directory_name = "period_types"
    item_name = "index"
    period_type_id = _get_directory_id(db, directory_name, item_name)
    # ic(owner_id, period_type_id)
    for line in monitors:
        data = _extract_monitoring_data_from_line(db, line, owner_id, period_type_id)
        row_id = _insert_period(db, data)
        if row_id is None:
            ic(tuple(line))
    return 0




def _parsing_raw_periods_from_csv(csv_file: str, db_file: str) -> int:
    """
    Читает данные о периодах из csv-файла выгруженного из Postgres Normative
    larix.period в SQLite tblRawDat.  Удаляет все данные из таблицы
    периодов tblPeriods. Загружает периоды типа "Дополнение" и "Индекс"
    для раздела 'ТСН' и 'Оборудование'.
    """
    _load_csv_to_raw_table(csv_file, db_file, delimiter=",")
    with SQLiteDB(db_file) as db:
        # Удалить все периоды !!! в tblPeriods
        db.go_execute(sql_sqlite_periods["delete_all_data_periods"])
        # переносим ТСН периоды
        _ton_supplement_periods_parsing(db)
        _ton_index_periods_parsing(db)
        # переносим периоды Мониторинга
        _monitoring_periods_parsing(db)

    # создаем ссылки на предыдущее дополнения
    _create_supplement_chain_periods(db_file)
    # создаем ссылки на предыдущее индексы и родительские дополнения
    _create_index_chain_periods(db_file)
    # создаем ссылки на предыдущее периоды мониторинга
    _create_monitoring_chain_periods(db_file)

    return 0

def get_periods_from_larix(db_file: str, csv_file: str) -> int:
    """Экспортирует данные о периодах из таблицы larix.periods в таблицу tblPeriods."""
    #
    # для создания БД надо запустить DB_support.create_support_db.py
    #
    # экспортируются все периоды: дополнения и индексы
    _export_table_periods_to_csv(csv_file, ais_access)
    # 
    _parsing_raw_periods_from_csv(csv_file, db_file)
    return 0

if __name__ == "__main__":
    #
    get_periods_from_larix(DB_FILE, PERIOD_CSV_FILE)
