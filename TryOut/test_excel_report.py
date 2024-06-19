
from models import ExcelBase,  ExcelReport

with ExcelReport("test.xlsx") as file:
    print(file.workbook)
    print(file.workbook.sheetnames)
    print(file.worksheet)
    # sheet = file.get_sheet(sheet_name, 0)
    # print(sheet)
