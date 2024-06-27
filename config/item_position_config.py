from typing import Any
from collections import namedtuple

ValuePosition = namedtuple(
    "ValuePosition", ["column_number", "column_letter", "value"], defaults=[0, None, None]
)
regular_story_length = 4


ITEM_POSITION: dict[str, ValuePosition|None] = {
    "row_count": ValuePosition(1, "A", 0),
    "code": ValuePosition(2, "B", ""),
    "name": ValuePosition(3, "C", ""),
    "base_price": ValuePosition(4, "D", ""),
    "price_history_range": ValuePosition(5, "E"),
    "last_period_delivery": ValuePosition(regular_story_length + 1),
    "check_need": ValuePosition(regular_story_length + 2),
    "supplier_price": ValuePosition(regular_story_length + 3),
    "is_delivery_included": ValuePosition(regular_story_length + 4),
    "transport_code": ValuePosition(regular_story_length + 5),
    "transport_base_price": ValuePosition(regular_story_length + 6),
    "transport_numeric_ratio": ValuePosition(regular_story_length + 7),
    "transport_actual_price": ValuePosition(regular_story_length + 8),
    "gross_weight": ValuePosition(regular_story_length + 9),
    "unit_measure": ValuePosition(regular_story_length + 10),
    "current_selling_price": ValuePosition(regular_story_length + 11),
    "empty_1": ValuePosition(regular_story_length + 12),
    # 
    "transport_price": ValuePosition(regular_story_length + 13),
    "result_price": ValuePosition(regular_story_length + 14),
    "previous_index": ValuePosition(regular_story_length + 15),
    "result_index": ValuePosition(regular_story_length + 16),
    "index_change_absolute": ValuePosition(regular_story_length + 17),
    "index_change_in_percentage": ValuePosition(regular_story_length + 18),
    # 
    "empty_2": ValuePosition(regular_story_length + 19),
    "absolute_price_change": ValuePosition(regular_story_length + 20),
    "percentage_price_change": ValuePosition(regular_story_length + 21),
    # 
    # "delivery_history_range": None
    # "abbe_criterion": ValuePosition(regular_story_length + 20),
}
