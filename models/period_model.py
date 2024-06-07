from collections import namedtuple

MiniPeriod = namedtuple(
    typename="MiniPeriod",
    field_names=["period_larix_id", "period_name"],
    defaults=[0, ""],
)

MiniPeriod.__annotations__ = {
    "period_larix_id": int,
    "period_name": str,
}


if __name__ == "__main__":
    p = MiniPeriod(151427079, "Дополнение 69")

    print(p.__dir__())
    print(p._asdict())
    print(p._fields)
    d=p._asdict()
    print(d)
