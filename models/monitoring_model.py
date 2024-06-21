from collections import namedtuple
from models.product_model import Product, ProductType

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

#
# class MonitoringMaterial:
# модель данных.
# Для периода дополнения SP и индексного периода IP
# Из отчета мониторинга берется список материалов.
# доступные материалы берутся для SP. Цены и другие данные берутся для IP.
class MonitoringMaterial(Product):
    def __init__(
        self,
        product_type: str,
        product_code: str,
        product_description: str,
        unit_measure: str,
        supplier_price: float,
        is_delivery_included: bool,
        description: str,
        #
        price_history: list[MonitoringPrice] = None,
    ):
        super().__init__(
            product_type, product_code, product_description, unit_measure
        )
        self.supplier_price = supplier_price
        self.is_delivery_included = is_delivery_included
        self.description = description
        self.price_history = price_history

    def __repr__(self):
        return (
            f"{type(self).__name__}(product_type={self.product_type!r}, "
            f"code={self.code!r}, "
            f"description={self.description!r}, "
            f"unit_measure={self.unit_measure!r}, "
            f"supplier_price={self.supplier_price!r}, "
            f"is_delivery_included={self.is_delivery_included!r}, "
            f"description={self.description!r}, "
            f"price_history={self.price_history!r})"
        )

if __name__ == "__main__":
    p = MonitoringPrice()
    print(p.__dir__())
    print(p._asdict())
    print(p._fields)

    p = Product(
        ProductType.MATERIAL,
        "1.1-1-5",
        "Алюминий сернокислый",
        "кг",
    )

    m = MonitoringMaterial(
        ProductType.MATERIAL,
        "1.1-1-5",
        "Алюминий сернокислый",
        "кг",
        #
        supplier_price=65.0,
        is_delivery_included=False,
        description="Алюминий сернокислый V34",
        price_history=[],
    )

    print(m)
