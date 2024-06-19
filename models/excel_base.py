import openpyxl

from common_features.message import output_message_exit, output_message
from common_features.files_features import (
    does_file_exist,
    is_file_in_use,
)


class ExcelBase:
    def __init__(self, file_path: str = None, sheet_name: str = None):
        self.file_path = file_path
        self.sheet_name = sheet_name
        self.workbook = None
        self.worksheet = None

    def __enter__(self):
        self.open_workbook()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.close_workbook()

    def open_workbook(self):
        if is_file_in_use(self.file_path):
            raise IOError(f"{self.file_path} file is being used by another program.")
        try:
            self.workbook = openpyxl.load_workbook(self.file_path)
            self.worksheet = self.workbook[self.sheet_name] if self.sheet_name else self.workbook.active
        except FileNotFoundError:
            self.workbook = openpyxl.Workbook()




    def close_workbook(self):
        if self.workbook:
            self.workbook.save(self.file_path)
            self.workbook.close()

    def get_filter_line(self):
        if self.worksheet and self.worksheet.auto_filter:
            filter_range = self.worksheet.auto_filter.ref
            filter_line = int(filter_range.split(":")[1].split()[0])
            return filter_line
        else:
            return None

    def clear_filters(self):
        """Очищает все фильтры, примененные к рабочему листу."""
        if self.worksheet and self.worksheet.auto_filter:
            self.worksheet.auto_filter.ref = None

    def get_column_index(self, column_name: str) -> int | None:
        """Возвращает индекс столбца по букве."""
        try:
            return self.worksheet.column_dimensions[column_name.upper()].index - 1
        except KeyError:
            return None
