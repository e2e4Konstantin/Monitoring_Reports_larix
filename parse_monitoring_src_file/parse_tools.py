import pandas
from icecream import ic
#
from config import DB_FILE
#
from common_features import (
    output_message_exit,
    clean_code,
    clean_text,
    is_quote_code,
    get_float,
    construct_absolute_file_path,
)

#
from parse_monitoring_src_file.excel_config import SourceData
#
from parse_monitoring_src_file.src_file_settings import (
    PRICE_COLUMN_DELTA,
    HEADER_HEIGHT,
    RELATIVE_CODE_POSITION,
    spelling_variations_delivery,
    anchors,
)


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
    search_text = anchors["materials_base_column_value"].lower()
    anchor_position = data.find_cell_with_cleaning(search_text)
    if not anchor_position:
        output_message_exit(
            f"Не найдена 'якорная' ячейка: {search_text!r}",
            f"файл: {excel_file!r} таблица: {sheet_name!r}",
        )
        return None
    column_number = data.cols_index[anchor_position.column] + PRICE_COLUMN_DELTA
    start_row = data.look_number_below(
        anchor_position.row + HEADER_HEIGHT, column_number
    )
    for row in range(start_row, data.row_max + 1):
        code = clean_code(
            data.get_cell_value_by_index(row, column_number - RELATIVE_CODE_POSITION)
        )
        if not code:
            continue
        if is_quote_code(code):
            raw_value = data.get_cell_value_by_index(row, column_number)
            supplier_price = get_float(raw_value)
            if (
                supplier_price
                and isinstance(supplier_price, float)
                and supplier_price > 0
            ):
                raw_delivery = clean_text(
                    data.get_cell_value_by_index(row, column_number + 6)
                )
                delivery = raw_delivery.lower() in spelling_variations_delivery
                material_name = clean_text(
                    data.get_cell_value_by_index(row, column_number - 7)
                )
                result.append((code, supplier_price, delivery, material_name))
            else:
                output_message_exit(
                    f"Шифр не соответствует шаблону: {supplier_price}",
                    f"цена поставщика в строке {row}",
                )
        else:
            output_message_exit(f"шифр в строке {row}", f"Не соответствует шифру расценки: {code!r}")
    return result if result else None


def parse_monitoring_material_file(data: dict[str:str]) -> int | None:
    """Разбирает файл с ценами на материалы для мониторинга."""
    source_file = data["src_file"]
    sheet_name = data["sheet_name"]

    result = _get_monitoring_material_data(source_file, sheet_name)
    df = pandas.DataFrame(result, columns=["code", "price", "delivery", "description"])
    print(df)
    # df.to_csv(result_file, sep=",", index=False)




if __name__ == "__main__":
    ic()
    # исходные данные
    src_material_path = r"C:\Users\kazak.ke\Documents\Задачи\5_Надя\исходные_данные\материалы"
    may_2024 = ("5_Отчет апрель 2024.xlsx", 72, 212, "приложение А")
    src_file = construct_absolute_file_path(src_material_path, may_2024[0])

    parse_monitoring_material_file(src_file)
