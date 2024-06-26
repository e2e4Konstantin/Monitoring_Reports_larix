
import pandas
import numpy
import string


from common_features import (
    output_message_exit,
    get_float,
    clean_string,
    does_file_exist,
)

from parse_monitoring_src_file.src_file_settings import CellPosition


class SourceData:
    def __init__(
        self, excel_file: str = None, sheet_name: str = None
    ) -> None:
        self.file = excel_file
        self.sheet_name = sheet_name
        self.df = pandas.DataFrame()
        self.row_max, self.column_max = 0, 0
        self.cols_index = None
        self.revers_cols = None
        self.check_file_name()
        self.get_data()

    def __str__(self):
        file_message = f"файл: {self.file!r}\nтаблица: {self.sheet_name!r}"
        size_message = f"строк: {self.row_max+1} столбцов: {self.column_max+1} "
        return f"{file_message}\nстолбец 'B': {self.df['B'].notnull().sum()} значений.\n{size_message}"

    def check_file_name(self):
        if not does_file_exist(self.file):
            output_message_exit(f"фйл: {self.file!r}", "Не найден.")

    def get_data(self):
        try:
            self.df = pandas.read_excel(
                self.file, self.sheet_name, header=None, dtype="object"
            )
            if not self.df.empty:
                self.row_max = self.df.shape[0] - 1
                self.column_max = self.df.shape[1] - 1
                self.set_column_names()
                self.cols_index = {x: i for i, x in enumerate(self.df.columns)}
                self.revers_cols = {value: key for key, value in self.cols_index.items()}
            else:
                raise TypeError(self.__class__)
        except Exception as err:
            output_message_exit(
                f"ошибка чтения данных из файла: {self.file!r}", f"{err}"
            )

    def get_cell_value(self, row_index: int, column_name: str) -> str:
        """Возвращает строковое значение ячейки."""
        if 0 <= row_index < self.row_max and (column_name in self.df.columns):
            value = self.df.at[row_index, column_name]
            if pandas.isna(value):
                return ""
            return str(value)
        return ""

    def get_cell_value_by_index(self, row_index: int, column_index: int) -> str:
        """Возвращает строковое значение ячейки."""
        if 0 <= row_index <= self.row_max and 0 <= column_index <= self.column_max:
            value = self.df.iat[row_index, column_index]
            if pandas.isna(value):
                return ""
            return str(value)
        return ""

    @staticmethod
    def generate_column_names(num_columns: int) -> tuple[str, ...] | None:
        """
        Возвращает кортеж с именами колонок, которые соответствуют буквенным именам колонок в excel.
        Указанной длинны.
        """
        if num_columns <= 0:
            raise ValueError(f"num_columns <= 0: {num_columns}")
        columns = list(string.ascii_uppercase)
        if len(columns) >= num_columns:
            return tuple(columns[:num_columns])
        gen = columns
        for char in columns:
            gen_next = tuple(char + c for c in columns)
            gen = (*gen, *gen_next)
            if len(gen) >= num_columns:
                return tuple(gen[:num_columns])
        return None


    def set_column_names(self):
        """ Назначить имена колонок в DF так как excel таблицах. Буквенные имена. """
        if self.df.empty or self.column_max < 1:
            raise ValueError(f"self.df пустой: {self}")
        self.df.columns = self.generate_column_names(self.df.shape[1])


    def find_cell(self, target: str) -> tuple[int, int] | None:
        """Найти координаты первого совпадения для значения в df"""
        rows, cols = numpy.where(self.df == target)
        if rows.size != 0 and cols != 0:
            return rows[0], cols[0]
        return None


    def find_cell_pd(self, value: str) -> tuple[int, int] | None:
        """Найти координаты первого совпадения для значения в df"""
        match = self.df.eq(value).idxmax()
        if match.size:
            return match
        return None

    def find_cell_with_cleaning(self, target_text: str) -> CellPosition | None:
        """ Ищет ячейку с нужным значением возвращает координаты """
        if self.df.empty or self.column_max < 1:
            raise ValueError(f"self.df is empty: {self.df}")
        for row in range(0, self.row_max + 1):
            for column in self.df.columns:
                value = clean_string(self.get_cell_value(row, column))
                if value.lower() == target_text.lower():
                    return CellPosition(row, column)
        return None

    def look_number_below(self, start_row: int, column: int) -> int | None:
        """ Найти первое число в столбце начиная со строки row.
        Если найдет то вернет номер строки."""
        for row in range(start_row, self.row_max + 1):
            value = self.get_cell_value_by_index(row, column)
            if pandas.isna(value):
                continue
            number = get_float(value)
            if isinstance(number, float):
                return row
        return None
