
from config import DB_FILE

from DB_support import create_new_monitoring_period, create_new_ton_index_period


if __name__ == "__main__":
    
    # создать новый период мониторинга
    period_id = create_new_monitoring_period(
        DB_FILE,
        previous_period="Апрель 2024",
        period_name="Мониторинг Май 2024 (212 сборник/дополнение 72)",
    )

    # создать новый индексный период ТСН
    period_id = create_new_ton_index_period(
            DB_FILE,
            supplement_number=72, 
            index_number=212, 
            name = "Индекс Май 2024/Дополнение 72 (мониторинг Апрель)",
            larix_id=167597127,
            )