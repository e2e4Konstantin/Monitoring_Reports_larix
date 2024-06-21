from collections import namedtuple
# Для хранения истории цен на материала мониторинга
MonitoringPrice = namedtuple(
    typename="MonitoringPrice",
    field_names=["period_name", "index_number", "price", "delivery"],
    defaults=[ None, 0, 0.0, False],
)

MonitoringPrice.__annotations__ = {
    "period_name": str,
    "index_number": int,
    "price": float,
    "delivery": bool,
}


class MonitoringMaterial:
    def __init__(
        self,
        code: str,
        period_name: str,
        supplier_price: float,
        is_transport_included: bool,
        description: str = None,
        price_history: list[MonitoringPrice] = None,
    ):
        self.code = code
        self.period_name = period_name
        self.supplier_price = supplier_price
        self.is_transport_included = is_transport_included
        self.description = description
        self.price_history = price_history

    def __repr__(self):
        return (
            f"{type(self).__name__}("
            f"code={self.code!r}, "
            f"period_name={self.period_name!r}, "
            f"current_price={self.supplier_price!r}, "
            f"is_transport_included={self.is_transport_included!r}, "
            f"description={self.description!r})"
        )

if __name__ == "__main__":
    p = MonitoringPrice()

    print(p.__dir__())
    print(p._asdict())
    print(p._fields)


