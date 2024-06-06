

class StorageCost:
    def __init__(
        self,
        storage_cost_rate: float,
        storage_cost_name: str,
        storage_cost_description: str,
    ):
        self.storage_cost_rate = storage_cost_rate
        self.storage_cost_name = storage_cost_name
        self.storage_cost_description = storage_cost_description

    def __repr__(self):
        return f"{type(self).__name__}({self.storage_cost_name!r}, {self.storage_cost_rate!r}, {self.storage_cost_description!r})"


if __name__ == "__main__":
    from icecream import ic

    sc = StorageCost(
        2.0,
        "Строй_мат, 2%",
        "к строительным материалам, кроме металлических конструкций",
    )
    ic(sc)
