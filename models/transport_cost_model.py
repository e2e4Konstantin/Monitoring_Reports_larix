from config import ROUNDING


class TransportCost:
    def __init__(
        self,
        transport_code: str,
        transport_name: str,
        transport_base_price: float,
        transport_current_price: float
    ):
        self.transport_code = transport_code
        self.transport_name = transport_name
        self.transport_base_price = transport_base_price
        self.transport_current_price = transport_current_price
        self.transport_inflation_rate = (
            round(transport_current_price / transport_base_price, ROUNDING)
            if transport_base_price > 0
            else 0.0
        )

    def __repr__(self):
        return f"{type(self).__name__}({self.transport_code}, {self.transport_name}, {self.transport_base_price}, {self.transport_current_price}, {self.transport_inflation_rate})"


if __name__ == "__main__":
    from icecream import ic

    t = TransportCost(
        "1.0-3-15",
        "Строительные грузы 1 класса, перевозимые бортовыми автомобилями: кирпич полнотелый",
        42.70000000,
        509.75000000,
    )
    ic(t)
