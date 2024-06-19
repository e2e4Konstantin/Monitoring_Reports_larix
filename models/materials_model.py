
from config import ROUNDING
from models.product_model import Product, ProductType
from models.transport_cost_model import TransportCost
from models.storage_cost_model import StorageCost
from models.monitoring_model import MonitoringMaterial

class Material(Product, TransportCost):
    def __init__(
        self,
        product_type: str = None,
        product_code: str = None,
        product_description: str = None,
        unit_measure: str = None,
        #
        net_weight: float = 0.0,
        gross_weight: float = 0.0,
        base_price: float = 0.0,
        current_price: float = 0.0,
        #
        transport_code: str = None,
        transport_name: str = None,
        transport_base_price: float = 0.0,
        transport_current_price: float = 0.0,
        #
        storage_cost_rate: float = 0.0,
        storage_cost_name: str = None,
        storage_cost_description: str = None,
        monitoring: MonitoringMaterial = None
    ):
        Product.__init__(
            self,
            product_type,
            product_code,
            product_description,
            unit_measure
        )
        TransportCost.__init__(
            self, transport_code, transport_name, transport_base_price, transport_current_price
        )
        StorageCost.__init__(
            self, storage_cost_rate, storage_cost_name, storage_cost_description
        )
        self.net_weight = net_weight
        self.gross_weight = gross_weight
        self.base_price = base_price
        self.current_price = current_price
        self.inflation_rate = (
            round(self.current_price / self.base_price, ROUNDING)
            if self.base_price > 0
            else 0.0
        )
        self.monitoring: MonitoringMaterial = monitoring
    def get_history_length(self) -> int | None:
        """Возвращает длину истории цен."""
        return len(self.monitoring.price_history) if self.monitoring.price_history else None


    def __repr__(self):
        repr_str = (
            f"{self.__class__.__name__}("
            f"product_type={self.product_type!r}, "
            f"code={self.code!r}, "
            f"description={self.description!r}, "
            f"unit_measure={self.unit_measure!r}, "
            f"gross_weight={self.gross_weight}, "
            f"net_weight={self.net_weight}, "
            f"base_price={self.base_price}, "
            f"current_price={self.current_price}, "
            f"inflation_rate={self.inflation_rate}, "
            f"transport_code={self.transport_code!r}, "
            f"transport_name={self.transport_name!r}, "
            f"transport_base_price={self.transport_base_price}, "
            f"transport_current_price={self.transport_current_price}, "
            f"transport_inflation_rate={self.transport_inflation_rate}, "
            f"storage_cost_rate={self.storage_cost_rate}, "
            f"storage_cost_name={self.storage_cost_name!r}, "
            f"storage_cost_description={self.storage_cost_description!r}, "
            f"monitoring={self.monitoring}"
            f")"
        )
        return repr_str


if __name__ == "__main__":
    from icecream import ic
    # ic(dir(Material))
    m = Material(
        ProductType.MATERIAL,
        "1.1-1-5",
        "Алюминий сернокислый",
        "кг",
        #
        net_weight=1.0,
        gross_weight=1.05,
        base_price=18.92000000,
        current_price=66.89000000,
        #
        transport_code="1.0-3-14",
        transport_name="Строительные грузы 1 класса, перевозимые бортовыми автомобилями: химическая продукция",
        transport_base_price=46.51000000,
        transport_current_price=555.27000000,
        storage_cost_rate=2.0,
        storage_cost_name="Строй_мат, 2%",
        storage_cost_description="к строительным материалам, кроме металлических конструкций",
    )
    ic(m)
    ic(m.__dict__)
    ic(m.__dict__.keys())

