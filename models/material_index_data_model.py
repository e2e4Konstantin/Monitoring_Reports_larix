


from models.transport_cost_model import TransportCost
from models.storage_cost_model import StorageCost






class MaterialIndexData(TransportCost, StorageCost):
    def __init__(
        self,
        base_price: float,
        current_price: float,
        inflation_rate: float,
        #
        net_weight: float = 0.0,
        gross_weight: float = 0.0,
        #
        transport_code: str = None,
        transport_name: str = None,
        transport_base_price: float = 0.0,
        transport_current_price: float = 0.0,
        #
        storage_cost_rate: float = 0.0,
        storage_cost_name: str = None,
        storage_cost_description: str = None
    ):
        TransportCost.__init__(
            self, transport_code, transport_name, transport_base_price, transport_current_price
        )
        StorageCost.__init__(
            self, storage_cost_rate, storage_cost_name, storage_cost_description
        )
        #
        self.base_price = base_price
        self.current_price = current_price
        self.inflation_rate = inflation_rate
        #
        self.net_weight = net_weight
        self.gross_weight = gross_weight




    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"base_price={self.base_price}, "
            f"current_price={self.current_price}, "
            f"gross_weight={self.gross_weight}, "
            f"net_weight={self.net_weight}, "
            f"inflation_rate={self.inflation_rate}, "
            f"transport_code={self.transport_code}, "
            f"transport_name={self.transport_name}, "
            f"transport_base_price={self.transport_base_price}, "
            f"transport_current_price={self.transport_current_price}, "
            f"transport_inflation_rate={self.transport_inflation_rate}, "
            f"storage_cost_rate={self.storage_cost_rate}, "
            f"storage_cost_name={self.storage_cost_name}, "
            f"storage_cost_description={self.storage_cost_description}"
            ")"
        )

if __name__ == "__main__":
    from icecream import ic
    # ic(dir(Material))
    m = MaterialIndexData(
        base_price=18.92,
        current_price=66.89,
        inflation_rate=0.0,
        net_weight=1.0,
        gross_weight=1.05,
        transport_code="1.0-3-14",
        transport_name="Строительные грузы 1 класса, перевозимые бортовыми автомобилями: химическая продукция",
        transport_base_price=46.51,
        transport_current_price=555.27,
        storage_cost_rate=2.0,
        storage_cost_name="Строй_мат, 2%",
        storage_cost_description="к строительным материалам, кроме металлических конструкций",
    )
    ic(m)
    ic(m.__dict__)
    ic(m.__dict__.keys())

