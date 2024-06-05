
from typing import Optional
from models.product_model import Product, ProductType


class Material(Product):
    def __init__(
        self,
        product_type,
        product_code,
        product_description,
        unit_measure,
        material_base_price: Optional[float] = 0.0,
        material_price: Optional[float] = 0.0,
    ):
        super().__init__(
            product_type,
            product_code,
            product_description,
            unit_measure,
        )
        self.base_price = material_base_price
        self.actual_price = material_price

    def __repr__(self):
        return f"{type(self).__name__}({self.product_type}, {self.code}, {self.description}, {self.unit_measure}, {self.base_price}, {self.actual_price})"

if __name__ == "__main__":
    from icecream import ic

    m = Material(
        ProductType.MATERIAL,
        "1.1-1-5",
        "Алюминий сернокислый",
        "кг",
        18.92000000,
        66.89000000,
    )
    ic(m)
