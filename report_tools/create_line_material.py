from icecream import ic
from openpyxl.utils import get_column_letter
from models import Material, MonitoringPrice
import itertools

def create_price_history_range(
    monitoring_prices: list[MonitoringPrice] = None, max_length: int = 0
) -> list[float | None]:
    """Создайте список цен. Если длина меньше max_length, заполните None."""
    empty_range = [None] * max_length
    if not monitoring_prices:
        return empty_range
    prices = [price.price for price in monitoring_prices]
    if len(prices) >= max_length:
        return prices[-max_length:]
    return empty_range[:len(prices)] + prices




def create_line_material(material: Material, row_number: int, max_history_len: int):
    """ Создать строку с данными о материале."""
    price_range = create_price_history_range(
        material.monitoring.price_history, max_history_len
    )
    pos = {
        "row_count": [1, 0],
        "code": [2, material.code],
        "name": [3, material.description],
        "base_price": [4, material.base_price],
        #
        "history range": [5, price_range],
    }
    history_end_column = pos["history range"][0] + len(price_range)-1
    # транспорт последнего  истории периода
    pos["last_period_delivery"] = [
        history_end_column + 1,
        "+" if material.monitoring.price_history[-1].delivery else "",
    ]
    pos["check_need"] = [
        history_end_column + 2,
        1 if material.monitoring.is_transport_included != material.monitoring.price_history[-1].delivery else "",
    ]
    pos["supplier_price"] = [history_end_column + 3, material.monitoring.supplier_price]
    pos["is_transport_included"] = [
        history_end_column + 4,
        "+" if material.monitoring.is_transport_included else "",
    ]
    pos["transport_code"] = [history_end_column + 5, material.transport_code]
    pos["transport_base_price"] = [
        history_end_column + 6,
        material.transport_base_price,
    ]
    pos["transport_numeric_ratio"] = [
        history_end_column + 7,
        material.transport_inflation_rate,
    ]
    pos["transport_actual_price"] = [
        history_end_column + 8,
        material.transport_current_price,
    ]
    pos["gross_weight"] = [history_end_column + 9, material.gross_weight]
    pos["unit_measure"] = [history_end_column + 10, material.unit_measure]
    pos["empty_1"] = [history_end_column + 11, ""]
    # формулы
    pos["transport_price"] = [history_end_column + 12, -77]
    pos["result_price"] = [history_end_column + 13, -77]
    pos["previous_index"] = [history_end_column + 14, -77]
    pos["result_index"] = [history_end_column + 15, -77]
    pos["abbe_criterion"] = [history_end_column + 16, -77]
    pos["absolute_price_change"] = [history_end_column + 17, -77]

    # добавляем букву для номера колонки
    for key in pos.keys():
        pos[key].append(get_column_letter(pos[key][0]))
    pos["transport_price"][1] = (
        f"={pos['transport_base_price'][2]}{row_number}*{pos['transport_numeric_ratio'][2]}{row_number}*{pos['gross_weight'][2]}{row_number}/1000"
    )
    # формулы
    # formulas = [
    #     f"={pos['transport_base_price'][2]}{row_number}*{pos['transport_numeric_ratio'][2]}{row_number}*{pos['gross_weight'][2]}{row_number}/1000",
    #     f"=ROUND(IF({pos['transport_flag'][2]}{row_number}, ({pos['monitoring_price'][2]}{row_number}-{pos['transport_price'][2]}{row_number}), {pos['monitoring_price'][2]}{row_number}),2)",
    #     f"={pos['actual_price'][2]}{row_number}/{pos['base_price'][2]}{row_number}",
    #     f"={pos['result_price'][2]}{row_number}/{pos['base_price'][2]}{row_number}",
    #     f"={pos['result_index'][2]}{row_number}-{pos['previous_index'][2]}{row_number}",
    #     f"=({pos['result_index'][2]}{row_number}/{pos['previous_index'][2]}{row_number})-1",
    #     "",
    #     material.abbe_criterion,
    #     f"=ROUND(ABS({pos['result_price'][2]}{row_number}-{pos['actual_price'][2]}{row_number}),3)",
    #     f'=IF({pos["absolute_price_change"][2]}{row_number}<=1.4*{pos["abbe_criterion"][2]}{row_number}, "", 1)',
    #     f"=({pos['result_price'][2]}{row_number}/{pos['actual_price'][2]}{row_number})-1",
    # ]
    # mod_row = [*data_pos[:-6], *formulas]
    ic(pos)
    d = dict(sorted(pos.items(), key=lambda x: x[1][0]))

    mod_row = [
        item
        for value in d.values()
        for item in (value[1] if isinstance(value[1], list) else [value[1]])
    ]


    ic(mod_row)
    return mod_row
