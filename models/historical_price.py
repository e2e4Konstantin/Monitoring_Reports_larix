
from collections import namedtuple

HistoricPrice = namedtuple(
    typename="HistoricPrice",
    field_names=["index_number", "base_price", "current_price"],
    defaults=[0, 0.0, 0.0],
)

HistoricPrice.__annotations__ = {
    "index_number": int, "base_price": float, "current_price": float
}


if __name__ == "__main__":
    p = HistoricPrice()

    print(p.__dir__())
    print(p._asdict())
    print(p._fields)
    