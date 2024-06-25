from common_features import construct_absolute_file_path

test_path = r"C:\Users\kazak.ke\Documents\Tmp"
src_material_path = r"C:\Users\kazak.ke\Documents\Задачи\5_Надя\исходные_данные\материалы"

monitoring_src_paths = {
    "Март 2024": {
        "file_name": "4_Глава_1_раздел0_тарифы_ для Доп_72_2 кв 2024 - данные 2024-04-18.xlsx",
        "sheet_name": "приложение А",
    },
    "Апрель 2024": {
        "file_name": "5_Отчет апрель 2024.xlsx",
        "sheet_name": "приложение А",
    },
    "Май 2024": {
        "file_name": "6_Отчет май 2024.xlsx",
        "sheet_name": "приложение А",
    },
    "Тест_2024": {
        "file_name": "5_Отчет_апрель_2024_short.xlsx",
        "sheet_name": "приложение А",
        "monitoring_file": construct_absolute_file_path(
            test_path, "5_Отчет_апрель_2024_short.xlsx"
        ),
    },
}


for period_name, period_data in monitoring_src_paths.items():
    if period_name == "Тест_2024":
        continue
    period_data["monitoring_file"] = construct_absolute_file_path(
        src_material_path, period_data["file_name"]
        )
    # print(period_data)

# for period_name, period_data in monitoring_src_paths.items():
#     print(period_name, period_data)