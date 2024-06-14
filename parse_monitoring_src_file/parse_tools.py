import pandas
from icecream import ic
#
from config import DB_FILE
from DB_support import SQLiteDB

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




def parse_monitoring_material_file(data: SrcFileData, db_file: str, table_name: str) -> int | None:
    """
    Разбирает файл с ценами на материалы для мониторинга.
    Загружает данные в таблицу table_name базы данных db_file.
    """
    materials = _get_monitoring_material_data(data.file_name, data.sheet_name)
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




if __name__ == "__main__":
    ic()
    # исходные данные
    src_material_path = r"C:\Users\kazak.ke\Documents\Tmp"
    src_file_name = "5_Отчет_апрель_2024_short.xlsx"
    src_file = construct_absolute_file_path(src_material_path, src_file_name)
    src_data = SrcFileData(
        file_name=src_file,
        sheet_name="приложение А",
        supplement_number=72,
        index_number=212,
    )
    # разобрать файл и записать в tblRawData sqlite
    parse_monitoring_material_file(src_data, DB_FILE, "tblRawData")
