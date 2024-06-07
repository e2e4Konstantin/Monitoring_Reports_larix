import re
import itertools


class Code:
    def __init__(self, code: str = None):
        self.code = code
        self.digit_code = self.code_to_number(code)

    @classmethod
    def split(cls, src_code: str = None) -> tuple[str, ...] | None:
        """Разбивает шифр на части. '4.1-2-10' -> ('4', '1', '2', '10')."""
        return tuple(part for part in re.split("[.-]", src_code) if part) if src_code else None

    @classmethod
    def split_int(cls, src_code: str = None) -> tuple[int, ...] | None:
        """Разбивает шифр на части из чисел. '4.1-2-10' -> (4, 1, 2, 10)."""
        parts = cls.split(src_code)
        return tuple(map(int, parts)) if parts else None

    @classmethod
    def code_to_number(cls, src_code: str) -> int|None:
        """Преобразует шифр в число. '3.1-2-99 ' -> 3001002099000000000
        sys.maxsize = 9223372036854775807
        2**63-1 == 9223372036854775807"""
        N = 3  # разрядов на группу
        GROUP_NUMBER = 6  # количество групп
        if src_code and isinstance(src_code, str):
            factors = tuple([10**x for x in range((GROUP_NUMBER - 1) * N, -N, -N)])
            splitted_code = cls.split_int(src_code)
            if len(splitted_code) > 1 and not all([x == 0 for x in splitted_code[1:]]):
                pairs = list(itertools.zip_longest(splitted_code, factors, fillvalue=0))
                return sum(map(lambda x: x[0] * x[1], pairs))
            else:
                return splitted_code[0] * factors[0] + len(splitted_code[1:])
        return None


if __name__ == "__main__":
    from icecream import ic

    # ic(dir(Code))
    m = Code("1.1-1-5")
    ic(m)
    ic(m.__dict__)
    ic(m.__dict__.keys())
