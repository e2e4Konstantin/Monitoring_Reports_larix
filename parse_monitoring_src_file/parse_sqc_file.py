

import pandas
from icecream import ic
#

from DB_support import (
    SQLiteDB,
    sql_sqlite_periods,
    sql_sqlite_monitoring,
    sql_sqlite_queries,
    create_new_monitoring_period,
)

#
from common_features import (
    output_message_exit,
    clean_code,
    clean_text,
    is_quote_code,
    get_float,
    construct_absolute_file_path,
    code_to_number,
)

#
from parse_monitoring_src_file.excel_config import SourceData
from DB_support import sql_sqlite_queries

#
from parse_monitoring_src_file.src_file_settings import (
    PRICE_COLUMN_DELTA,
    HEADER_HEIGHT,
    RELATIVE_CODE_POSITION,
    spelling_variations_delivery,
    anchors,
    SrcFileData,
    CellPosition,
)


def search_text_in_data(data: SourceData, search_text: str) -> CellPosition | None:
    """ Ищет ячейку с нужным значением возвращает координаты. """
    position: CellPosition = data.find_cell_with_cleaning(search_text.lower())
    if not position:
        output_message_exit(
            f"Не найдена 'якорная' ячейка: {search_text!r}",
            f"файл: {data.file!r} таблица: {data.sheet_name!r}",
        )
        return None
    return position


def _get_monitoring_material_data(excel_file: str, sheet_name: str) -> list[tuple[str, float, str]] | None:
    """
    Получить данные из файла мониторинга.
    Возвращает список кортежей (шифр, 'отпускная цена поставщика', 'описание материала')
    Находит якорную колонку. Высчитывает столбец в котором записаны цены поставщика.
    Высчитывает строку с которой будет искать шифры расценок.
    Считывает шифр расценки и цену поставщика.
    """
    result = []
    data = SourceData(excel_file, sheet_name)
    base_cell = search_text_in_data(data, anchors["monitoring_base_column_value"])
    price_cell = search_text_in_data(data, anchors["monitoring_code_column_value"])
    delivery_cell = search_text_in_data(data, anchors["monitoring_delivery_column_value"])
    description_cell = search_text_in_data(data, anchors["monitoring_description_column_value"])
    #
    base_column = data.cols_index[base_cell.column]
    price_column = base_column + PRICE_COLUMN_DELTA
    code_column = data.cols_index[price_cell.column]
    delivery_column = data.cols_index[delivery_cell.column]
    description_column = data.cols_index[description_cell.column]
    #
    data_start_row = data.look_number_below(base_cell.row + HEADER_HEIGHT, base_column)
    #
    for row in range(data_start_row, data.row_max + 1):
        code = clean_code(data.get_cell_value_by_index(row, code_column))
        if not code:
            continue
        if is_quote_code(code):
            raw_price = data.get_cell_value_by_index(row, price_column)
            price = get_float(raw_price)
            if (price and isinstance(price, float) and price > 0):
                raw_delivery = clean_text(
                    data.get_cell_value_by_index(row, delivery_column)
                )
                delivery = raw_delivery.lower() in spelling_variations_delivery if raw_delivery else False
                description = clean_text(
                    data.get_cell_value_by_index(row, description_column)
                )
                result.append((code, price, delivery, description))
            else:
                output_message_exit(
                    f"Шифр не соответствует шаблону: {price}",
                    f"цена поставщика в строке {row}",
                )
        else:
            output_message_exit(f"шифр в строке {row}", f"Не соответствует шифру расценки: {code!r}")
    return result if result else None

def _add_raw_digit_code_to_raw_table(db_file: str):
    """Добавить поле digit_code в таблицу tblRawData и заполнить его."""
    with SQLiteDB(db_file) as db:
        db.go_execute(sql_sqlite_queries["add_digit_code_column_raw_table"])
        data = db.go_select(sql_sqlite_queries["select_all_raw_table"])
        for line in data:
            db.go_execute(
                sql_sqlite_queries["update_digit_code_raw_table"],
                ({"digit_code": code_to_number(line["code"]), "id": line["rowid"]}),
            )


def _load_df_to_sqlite_table(df: pandas.DataFrame, db_file: str, table_name: str) -> int:
    """Загружает данные из df в таблицу table_name базы данных db_file"""
    with SQLiteDB(db_file) as db:
        df.to_sql(
            name=table_name,
            con=db.connection,
            if_exists="replace",
            index=False,
            chunksize=100,
            method="multi",
        )  # dtype=pandas.StringDtype(),
        [result] = db.go_select(f"SELECT COUNT(*) AS count FROM {table_name};")
        count = result["count"]
        message = f"Из df импортировано: {count} записей в {table_name!r}"
        ic(message)
    return 0




def parse_monitoring_material_file(file_name: str, sheet_name: str, db_file: str, table_name: str) -> int | None:
    """
    Разбирает файл с ценами на материалы для мониторинга.
    Загружает данные в таблицу table_name базы данных db_file.
    """
    materials = _get_monitoring_material_data(file_name, sheet_name)
    materials_df = pandas.DataFrame(
        materials, columns=["code", "price", "delivery", "description"]
    )
    column_types = {"code": str, "price": float, "delivery": str, "description": str}
    materials_df = materials_df.astype(column_types)
    # print(materials_df.head())
    ic(materials_df.shape)
    ic(materials_df.columns)
    # ic(materials_df.dtypes)
    _load_df_to_sqlite_table(materials_df, db_file, table_name)
    _add_raw_digit_code_to_raw_table(db_file)

    return 0

def take_monitoring_report_file_inventory(
    db_file: str,
    period_id: int,
    report_monitoring_file: str,
    sheet_name: str = "приложение А",
)-> int | None:
    """ Добавляет данные о файле отчета мониторинга в таблицу tblMonitorFiles. """
    with SQLiteDB(db_file) as db:
        query = sql_sqlite_periods["select_by_id"]
        [period] = db.go_select(query, {"period_id": period_id})
        period_name = period["comment"]
        ic(period["id"], period_name)

        db.go_execute(
            sql_sqlite_monitoring["delete_monitoring_files_by_period_id"],
            {"period_id": period_id}
        )
        file_id = db.go_insert(
            sql_sqlite_monitoring["insert_monitoring_files"],
            {
                "period_id": period_id,
                "report_file": report_monitoring_file,
                "sheet_name": sheet_name,
                "period_name": period_name,
            },
            message=f"добавляем данные о файле отчета мониторинга {report_monitoring_file} в таблицу tblMonitorFiles",
        )
        return file_id

def save_the_monitoring_report(db_file: str, period_id: int, file_id: int) -> int:
    """Сохраняет данные о мониторинге из таблицы tblRawData
    в таблицу tblMonitoringMaterialsReports."""
    with SQLiteDB(db_file) as db:
        db.go_select(
            sql_sqlite_monitoring["delete_data_for_period_id"], {"period_id": period_id}
        )
        raw_monitoring_data = db.go_select(sql_sqlite_queries["select_all_raw_table"])
        for line in raw_monitoring_data:
            data = {
                    "period_id": period_id,
                    "file_id": file_id,
                    "code": line["code"],
                    "supplier_price": line["price"],
                    "delivery": line["delivery"],
                    "description": line["description"],
                    "digit_code": line["digit_code"],
                }
            db.go_insert(
                sql_sqlite_monitoring["insert_monitoring_item"], data,
                message=f"добавляем данные о материале {line['code']} в таблицу tblMonitoringMaterialsReports"
            )
    return 0


def get_period_id_by_comment(db_file: str, period_comment: str) -> int | None:
    """Возвращает id периода мониторинга по его комментарию."""
    with SQLiteDB(db_file) as db:
        query = sql_sqlite_periods["select_monitoring_by_comment"]
        period = db.go_select(query, {"monitoring_comment": period_comment})
    return period[0]["id"] if period else None



def load_monitoring_data_file(period_name: str, monitoring_file: str, sheet_name: str, db_file: str) -> int:
    """Разбирает файл отчета мониторинга и сохраняет его в БД."""
    period_id = get_period_id_by_comment(db_file, period_name)
    if not period_id:
        message = f"Не найден период {period_name!r} в таблице 'tblPeriods'"
        output_message_exit(message, 'создай новый период мониторинга')
    # записать в БД данные о файле отчета мониторинга
    file_id = take_monitoring_report_file_inventory(
        db_file, period_id, monitoring_file, sheet_name
    )
    ic(file_id)
    # разобрать файл и записать в tblRawData sqlite
    parse_monitoring_material_file(monitoring_file, sheet_name, db_file, "tblRawData")
    # сохранить данные о мониторинге в таблицу tblMonitoringMaterialsReports
    save_the_monitoring_report(db_file, period_id, file_id)
    return 0

if __name__ == "__main__":
    from config import DB_FILE
    from parse_monitoring_src_file.path_source_files import monitoring_src_paths

    ic()
    period_name = "Апрель 2024"    # "Тест_2024" #"Май 2024"
    src_data = monitoring_src_paths[period_name]
    # period_name = "Апрель 2024"
    #
    # создать новый период мониторинга
    # period_id = create_new_monitoring_period(
    #     DB_FILE,
    #     previous_period="Апрель 2024",
    #     period_name="Мониторинг Май 2024 (212 сборник/дополнение 72)",
    # )

    # period_id = 70  # Апрель 2024
    # period_id = 126  # Май 2024

    load_monitoring_data_file(
        period_name,
        src_data["monitoring_file"],
        src_data["sheet_name"],
        db_file=DB_FILE,
    )


