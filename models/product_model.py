from enum import Enum

class ProductType(Enum):
    QUOTE = "quote"
    EQUIPMENT = "equipment"
    MATERIAL = "material"


class Product:
    def __init__(
        self,
        product_type: ProductType,
        product_code: str,
        product_description: str,
        unit_measure: str,
    ):
        self.product_type = product_type.value
        self.code = product_code
        self.description = product_description
        self.unit_measure = unit_measure

    def __repr__(self):
        return f"{type(self).__name__}({self.product_type}, {self.code}, {self.description}, {self.unit_measure})"

if __name__ == "__main__":
    from icecream import ic

    p = Product(
        ProductType.MATERIAL,
        "1.1-1-5",
        "Алюминий сернокислый",
        "кг",
    )
    ic(p)
