
from config import ROUNDING
from models.product_model import Product, ProductType
from models.transport_cost_model import TransportCost
from models.storage_cost_model import StorageCost


class Material(Product, TransportCost):
    def __init__(
        self,
        product_type: str = None,
        product_code: str = None,
        product_description: str = None,
        unit_measure: str = None,
        material_base_price: float = 0.0,
        material_current_price: float = 0.0,
        #
        transport_code: str = None,
        transport_name: str = None,
        transport_base_price: float = 0.0,
        transport_current_price: float = 0.0,
        #
        storage_cost_rate: float = 0.0,
        storage_cost_name: str = None,
        storage_cost_description: str = None,
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
        self.base_price = material_base_price
        self.current_price = material_current_price
        self.inflation_rate = (
            round(self.current_price / self.base_price, ROUNDING)
            if self.base_price > 0
            else 0.0
        )

    def __repr__(self):
        s1 = f"{type(self).__name__}({self.product_type!r}, {self.code!r}, {self.description!r}, {self.unit_measure!r},"
        s2 = f"{self.base_price!r}, {self.current_price!r}, {self.inflation_rate!r}, "
        s3 = f"{self.transport_code!r}, {self.transport_name!r}, {self.transport_base_price!r}, {self.transport_current_price!r}, {self.transport_inflation_rate!r}, "
        s4 = f"{self.storage_cost_rate!r}, {self.storage_cost_name!r}, {self.storage_cost_description!r}"
        return f"{type(self).__name__}({s1}{s2}{s3}{s4})"


if __name__ == "__main__":
    from icecream import ic

    m = Material(
        ProductType.MATERIAL,
        "1.1-1-5",
        "Алюминий сернокислый",
        "кг",
        18.92000000,
        66.89000000,
        transport_code="1.0-3-14",
        transport_name="Строительные грузы 1 класса, перевозимые бортовыми автомобилями: химическая продукция",
        transport_base_price=46.51000000,
        transport_current_price=555.27000000,
        storage_cost_rate=2.0,
        storage_cost_name="Строй_мат, 2%",
        storage_cost_description="к строительным материалам, кроме металлических конструкций",
    )
    ic(m)
