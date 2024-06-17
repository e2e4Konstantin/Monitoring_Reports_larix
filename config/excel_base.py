import openpyxl


from common_features import (
    output_message_exit,
    does_file_exist,
    is_file_in_use,
)


class ExcelBase:
    def __init__(self, excel_file: str = None, sheet_name: str = None):
        self.file = excel_file
        self.sheet_name = sheet_name
        self.book = None
        self.sheet = None

    def __enter__(self):
        """Вызывается при старте контекстного менеджера. Открывает книгу, создает листы."""
        self.open_file()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """Будет вызван в завершении конструкции with, или в случае возникновения ошибки после нее."""
        self.close_file()

    def __str__(self):
        return f"excel file: {self.file}, sheet: {self.book}, {self.sheet}"

    def open_file(self):
        """Открыть рабочую книгу"""
        if does_file_exist(self.file) and not is_file_in_use(self.file):
            try:
                self.book = openpyxl.load_workbook(self.file)
                self.sheet = self.book[self.sheet_name]
            except IOError:
                raise
        else:
            output_message_exit("open_excel_file >> Не могу открыть файл", self.file)

    def save_file(self):
        """Сохранить рабочую книгу в файл."""
        if self.is_file_in_use():
            # self.close_file()
            output_message_exit(
                "close_excel_file >> Не могу записать файл",
                f"{self.file} используется в другой программе.",
            )
        else:
            if self.book:
                self.book.save(self.file)

    def close_file(self):
        if self.book:
            self.book.close()

    def get_filter_line(self):
        if self.sheet and self.sheet.auto_filter:
            filter_range = self.sheet.auto_filter.ref
            filter_line = int(filter_range.split(":")[1].split()[0])
            return filter_line
        else:
            return None

    def clear_filters(self):
        """Очищает все фильтры, примененные к рабочему листу."""
        if self.sheet and self.sheet.auto_filter:
            self.sheet.auto_filter.ref = None

    def get_column_index(self, column_name: str) -> int | None:
        """Возвращает индекс столбца по букве."""
        try:
            return self.sheet.column_dimensions[column_name.upper()].index - 1
        except KeyError:
            return None
