from collections import namedtuple
from models.product_model import Product
from models.material_index_data_model import MaterialIndexData

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
        monitoring_description: str,
        #
        monitoring_price_history: list[MonitoringPrice] = None,
        index_period_material_data: MaterialIndexData = None,
    ):
        super().__init__(
            product_type, product_code, product_description, unit_measure
        )
        self.supplier_price = supplier_price
        self.is_delivery_included = is_delivery_included
        self.monitoring_description = monitoring_description
        self.monitoring_price_history = monitoring_price_history
        self.index_period_material_data = index_period_material_data

    def __repr__(self):
        return (
            f"{type(self).__name__}(product_type={self.product_type!r}, "
            f"code={self.code!r}, "
            f"description={self.monitoring_description!r}, "
            f"unit_measure={self.unit_measure!r}, "
            f"supplier_price={self.supplier_price!r}, "
            f"is_delivery_included={self.is_delivery_included!r}, "
            f"description={self.description!r}, "
            f"monitoring_price_history={self.monitoring_price_history})"
            f"index_period_material_data={self.index_period_material_data})"
        )

    def get_history_length(self) -> int | None:
        """Возвращает длину истории цен."""
        return len(self.monitoring_price_history) if self.monitoring_price_history else None


if __name__ == "__main__":
    from models.product_model import ProductType

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
        product_code="1.1-1-5",
        product_description="Алюминий сернокислый",
        unit_measure="кг",
        #
        supplier_price=65.0,
        is_delivery_included=False,
        monitoring_description="Алюминий сернокислый V34",
        monitoring_price_history=[],
        index_period_material_data=None,
    )

    print(m.__dir__())
    # f = ['product_type', 'code', 'digit_code', 'description', 'unit_measure', 
    #  'supplier_price', 'is_delivery_included', 'monitoring_description', 
    #  'monitoring_price_history', 
    #  'index_period_material_data']