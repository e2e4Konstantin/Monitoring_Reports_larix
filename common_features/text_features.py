import itertools

import re
from fastnumbers import isfloat, isint
from dateutil import parser


_re_compiled_patterns = {
    "wildcard": re.compile(r"[\t\n\r\f\v\s+]+"),
    "code_valid_chars": re.compile(r"[^\d+.-]+"),
    "digits": re.compile(r"[^\d+]+"),
    "digits_dots": re.compile(r"[^\d+.]+"),
}


def remove_wildcard(source: str = None) -> str | None:
    """Удаляет из строки переносы строк и табуляции, одиночные пробелы оставляет"""
    return (
        re.sub(_re_compiled_patterns["wildcard"], r" ", source.strip())
        if source
        else None
    )


def clear_code(source: str = None) -> str | None:
    """Удаляет из строки все символы кроме (чисел, '.', '-')"""
    return re.sub(_re_compiled_patterns["code_valid_chars"], r"", source)


def keep_just_numbers(source: str = None) -> str | None:
    """Удаляет из строки все символы кроме чисел"""
    if source:
        return re.sub(_re_compiled_patterns["digits"], r"", source)
    return ""


def keep_just_numbers_dots(source: str = None) -> str | None:
    """Удаляет из строки все символы кроме чисел и точек"""
    if source:
        return re.sub(_re_compiled_patterns["digits_dots"], r"", source)
    return ""


def clean_text(text: str) -> str | None:
    """Удаляет из строки служебные символы и лишние пробелы."""
    text = remove_wildcard(text)
    return " ".join(text.split()) if text else None


def title_catalog_extraction(title: str, pattern_prefix: str) -> str | None:
    """Удаляет лишние пробелы. Удаляет из заголовка префикс. В первом слове делает первую букву заглавной."""
    title = clean_text(title)
    if title:
        return re.sub(pattern_prefix, "", title).strip().capitalize()
    return None


def split_code(src_code: str = None) -> tuple[str, ...] | None:
    """Разбивает шифр на части. '4.1-2-10' -> ('4', '1', '2', '10')"""
    return tuple([x for x in re.split("[.-]", src_code) if x]) if src_code else None


def split_code_int(src_code: str = None) -> tuple[int, ...] | None:
    """Разбивает шифр на части из чисел. '4.1-2-10' -> (4, 1, 2, 10)"""
    digit_string = split_code(src_code)
    ret = tuple(map(int, digit_string))
    return ret


def get_float_value(value: str) -> float:
    """Конвертирует строку в число с плавающей точкой."""
    if value:
        value = value.replace(",", ".", 1)
        return float(value) if isfloat(value) else 0.0
    return 0.0


def convert_to_integer(value: str) -> int:
    """Конвертирует строку в целое число."""
    return int(value) if isint(value) else 0


def parse_date(date_string: str) -> str | None:
    """Конвертирует строку в формат даты."""
    try:
        parsed_date = parser.parse(date_string)
        return parsed_date.strftime("%Y-%m-%d")
    except ValueError:
        return None


def date_to_numbers(date_str: str) -> tuple[int, int, int] | None:
    """Convert date string to year, month, day integers."""
    parsed_date = parse_date(date_str)
    if parsed_date:
        year, month, day = map(int, parsed_date.split("-"))
        return year, month, day


def code_to_number(src_code: str) -> int:
    """Преобразует шифр в число. '3.1-2-99 ' -> 3001002099000000000
    sys.maxsize = 9223372036854775807
    2**63-1 == 9223372036854775807"""
    N = 3  # разрядов на группу
    GROUP_NUMBER = 6  # количество групп
    if src_code and isinstance(src_code, str):
        factors = tuple([10**x for x in range((GROUP_NUMBER - 1) * N, -N, -N)])
        splitted_code = split_code_int(src_code)
        if len(splitted_code) > 1 and not all([x == 0 for x in splitted_code[1:]]):
            pairs = list(itertools.zip_longest(splitted_code, factors, fillvalue=0))
            return sum(map(lambda x: x[0] * x[1], pairs))
        else:
            return splitted_code[0] * factors[0] + len(splitted_code[1:])
    return 1


if __name__ == "__main__":
    from icecream import ic


    ic(date_to_numbers("2023-12-14"))


    # codes = (
    #     "1",
    #     "1.",
    #     "1.0",
    #     "1.0-0",
    #     "1.0-0-0",
    #     "1.0-0-0-0",
    #     "1.0-0-0-0-1",
    # )

    # # codes = ('1.', '10', '3', '3.0', '3.99', '3.1-99', '3.1-2-99',
    # #          '3.1-2-999', '3.1-2-3-999', '3.1-2-3-4-999', '999.999-999-999-999-999', '999.888-777-666-555-444-333')
    # for x in codes:
    #     print(f"{x:<15} {code_to_number(x)}")

    # print(f"'0.0-0-0' {code_to_number('0.0-0-0')}")