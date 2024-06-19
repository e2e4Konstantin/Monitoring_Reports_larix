
from openpyxl.utils import get_column_letter
from models import Material


def create_line_material(material: Material, row_number: int, max_history_len: int):
    """ Создать строку с данными о материале."""
    pos = {
        "row_count": [1, 0],
        "code": [2, material.code],
        "name": [3, material.name],
        "base_price": [4, material.base_price],
        #
        "history range": [5, None],
    }
    # вставляем пустые значения если история короче
    history_value = [x.history_price for x in material.history]
    if len(history_value) < max_history_len:
        for _ in range(max_history_len - len(history_value)):
            history_value.insert(0, None)
    else:
        history_value = history_value[-max_history_len:]
    #
    pos["history range"][1] = history_value
    history_end_column = pos["history range"][0] + len(history_value)
    #
    pos["index_num"] = [history_end_column, material.index_num]
    pos["actual_price"] = [history_end_column + 1, material.actual_price]
    pos["monitoring_index"] = [history_end_column + 2, material.monitoring_index]
    pos["monitoring_price"] = [history_end_column + 3, material.monitoring_price]
    #
    pos["history_freight_included"] = [
        history_end_column + 4,
        material.history_freight_included,
    ]
    pos["history_freight_not_included"] = [
        history_end_column + 5,
        material.history_freight_not_included,
    ]
    pos["history_check"] = [history_end_column + 6, material.history_check]
    #
    pos["transport_flag"] = [history_end_column + 7, material.transport_flag]
    pos["transport_code"] = [history_end_column + 8, material.transport_code]
    pos["transport_base_price"] = [
        history_end_column + 9,
        material.transport_base_price,
    ]
    pos["transport_numeric_ratio"] = [
        history_end_column + 10,
        material.transport_numeric_ratio,
    ]
    pos["transport_actual_price"] = [
        history_end_column + 11,
        material.transport_actual_price,
    ]
    #
    pos["gross_weight"] = [history_end_column + 12, material.gross_weight]
    pos["empty"] = [history_end_column + 13, ""]
    # формулы
    pos["transport_price"] = [history_end_column + 14, -77]
    pos["result_price"] = [history_end_column + 15, -77]
    pos["previous_index"] = [history_end_column + 16, -77]
    pos["result_index"] = [history_end_column + 17, -77]
    pos["abbe_criterion"] = [history_end_column + 21, material.abbe_criterion]
    pos["absolute_price_change"] = [history_end_column + 22, -77]
    #
    history_start_column = pos["history range"][0]
    history = {
        f"history_{i}": [history_start_column + i, v]
        for i, v in enumerate(pos["history range"][1])
    }
    # ic(history)
    pos.pop("history range")
    pos.update(history)

    for key in pos.keys():
        pos[key].append(get_column_letter(pos[key][0]))
    # формируем значения строки
    data = {value[0]: value[1] for value in pos.values()}
    data_pos = [data[x] for x in sorted(list(data.keys()))]
    # ic(data_pos)
    # ic(pos["transport_base_price"][0])
    # формулы
    formulas = [
        f"={pos['transport_base_price'][2]}{row_number}*{pos['transport_numeric_ratio'][2]}{row_number}*{pos['gross_weight'][2]}{row_number}/1000",
        f"=ROUND(IF({pos['transport_flag'][2]}{row_number}, ({pos['monitoring_price'][2]}{row_number}-{pos['transport_price'][2]}{row_number}), {pos['monitoring_price'][2]}{row_number}),2)",
        f"={pos['actual_price'][2]}{row_number}/{pos['base_price'][2]}{row_number}",
        f"={pos['result_price'][2]}{row_number}/{pos['base_price'][2]}{row_number}",
        f"={pos['result_index'][2]}{row_number}-{pos['previous_index'][2]}{row_number}",
        f"=({pos['result_index'][2]}{row_number}/{pos['previous_index'][2]}{row_number})-1",
        "",
        material.abbe_criterion,
        f"=ROUND(ABS({pos['result_price'][2]}{row_number}-{pos['actual_price'][2]}{row_number}),3)",
        f'=IF({pos["absolute_price_change"][2]}{row_number}<=1.4*{pos["abbe_criterion"][2]}{row_number}, "", 1)',
        f"=({pos['result_price'][2]}{row_number}/{pos['actual_price'][2]}{row_number})-1",
    ]
    mod_row = [*data_pos[:-6], *formulas]
    # ic(mod_row)
    return mod_row
