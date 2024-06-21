from models import MonitoringMaterial
from icecream import ic


def create_header(table: list[MonitoringMaterial], view_history_depth: int) -> str:
    """Создать заголовок таблицы отчета."""
    header = [
        "No",
        "шифр",
        "название",
        "базовая\nстоимость",
        #
        # -- история мониторинга
        "прошлый период транспорт включен",
        "нужна\nпроверка",
        "мониторинг\nцена поставщика",  # monitoring price
        "транспорт включен",  # transport flag
        "шифр транспорта",  # transport code
        "транспорт базовая цена",  # transport base price
        "транспорт коэффициент",  # transport numeric ratio
        "транспорт текущая цена",  # transport actual price
        #
        "вес брутто",  # gross weight
        "ед.изм",
    ]
    header_calculated = [
        ".",
        "стоимость перевозки",
        "цена для загрузки",
        "предыдущий индекс",
        "текущий индекс",
        "рост абс.",
        "рост %",
        ".",
        "критерий разниц пар",
        "абс.",
        "внимание",
        "процент рост/падение",
    ]

    history_sizes = set([material.get_history_length() for material in table])
    max_history_len = max(history_sizes)
    ic(max_history_len, history_sizes)  #  {1, 4, 5}
    if max_history_len > view_history_depth:
        max_history_len = view_history_depth

    history_header = []
    #  найти материал с длинной историей и записать заголовок
    for material in table:
        if material.get_history_length() >= max_history_len:
            # ic(material.monitoring.price_history)
            # ic(material.monitoring.price_history[-max_history_len:])
            history_header = [
                x.period_name
                for x in material.monitoring_price_history[-max_history_len:]
            ]
            # ic(history_header)
            break
    history_start = 4
    final_header = [
        *header[:history_start],
        *history_header,
        *header[history_start:],
        *header_calculated,
    ]
    return final_header, max_history_len
