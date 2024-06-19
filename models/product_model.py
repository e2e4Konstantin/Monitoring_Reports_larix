from enum import Enum
from models.code_model import Code


class ProductType(Enum):
    QUOTE = "quote"
    EQUIPMENT = "equipment"
    MATERIAL = "material"


class Product(Code):
    def __init__(self, product_type: ProductType, code: str, description: str, unit_measure: str):
        self.product_type = product_type.value
        super().__init__(code)
        self.description = description
        self.unit_measure = unit_measure


    def __repr__(self):
        return f"{self.__class__.__name__}(product_type={self.product_type!r}, code={self.code!r}, description={self.description!r}, unit_measure={self.unit_measure!r})"
if __name__ == "__main__":
    from icecream import ic

    p = Product(
        ProductType.MATERIAL,
        "1.1-1-5",
        "Алюминий сернокислый",
        "кг",
    )
    ic(p)
    ic(p.__dict__.keys())
