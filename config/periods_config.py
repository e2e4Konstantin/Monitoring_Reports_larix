
class BasePeriod:
    """Base class for a period."""
    def __init__(
        self,
        name: str,
        period_title: str,
        period_id: int,
        parent_id: int,
        regex_pattern: str,
    ):
        self.name = name
        self.period_title = period_title
        self.period_id = period_id
        self.parent_id = parent_id
        self.regex_pattern = regex_pattern

class SupplementPeriod(BasePeriod):
    """Supplement period."""
    def __init__(
        self,
        name: str,
        period_title: str,
        period_id: int,
        parent_id: int,
        regex_pattern: str,
        supplement_number: int,
    ) -> None:
        super().__init__(
            name=name,
            period_title=period_title,
            period_id=period_id,
            parent_id=parent_id,
            regex_pattern=regex_pattern,
        )
        self.supplement_number = supplement_number
    def __str__(self) -> str:
        return f"{self.name!r} {self.supplement_number} {self.period_id}"


class IndexPeriod(BasePeriod):
    """Index period."""
    def __init__(
        self,
        name: str,
        period_title: str,
        period_id: int,
        parent_id: int,
        regex_pattern: str,
        supplement_number: int,
        index_number: int,
    ) -> None:
        super().__init__(
            name=name,
            period_title=period_title,
            period_id=period_id,
            parent_id=parent_id,
            regex_pattern=regex_pattern,
        )
        self.supplement_number = supplement_number
        self.index_number = index_number
    def __str__(self) -> str:
        return f"{self.name!r} {self.index_number} {self.supplement_number} {self.period_id}"


# r"^\s*Дополнение\s*\d+\s*$"
# r"^\s*\d+\s*индекс/дополнение\s*\d+"

if __name__ == "__main__":
    supplement_72 = SupplementPeriod(
        name="Дополнение 72",
        period_title="Дополнение 72",
        period_id=166954793,
        parent_id=152472566,
        regex_pattern=r"^\s*Дополнение\s*71\s*$",
        #
        supplement_number=72,
    )
    index_211 = IndexPeriod(
        name="Индекс 211/72",
        period_title="211 индекс/дополнение 72 (мониторинг 2 кв 2024)",
        period_id=167403321,
        parent_id=167264731,
        regex_pattern=r"^\s*210\s*индекс/дополнение\s*\d+\s*\(мониторинг",
        #
        supplement_number=72,
        index_number=211,
    )

    print(supplement_72)
    print(index_211)
