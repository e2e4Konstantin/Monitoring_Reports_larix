import sqlite3
from datetime import datetime
from dateutil.relativedelta import relativedelta
from icecream import ic

from DB_support.db_config import SQLiteDB
from DB_support.sql_sqlite_periods import sql_sqlite_periods
from common_features import extract_monitoring_supplement_index_cmt, output_message_exit
from config import DB_FILE



def create_new_monitoring_period(db_file: str, previous_period: str, period_name: str)->int:
    """Создание нового периода мониторинга.
    "Мониторинг Сентябрь 2023 (204 сборник/дополнение 69)", "Апрель 2024"
    """
    with SQLiteDB(db_file) as db:
        [period] = db.go_select(
            sql_sqlite_periods["select_monitoring_by_comment"],
            {"monitoring_comment": previous_period},
        )
        ic(tuple(period))
        _, _, comment = extract_monitoring_supplement_index_cmt(period_name)
        supplement_number = period["supplement_number"]
        index_number = period["index_number"] + 1
        name = f"Мониторинг {comment} {index_number}/{supplement_number}"
        date = datetime.strptime(period["start_date"], "%Y-%m-%d").date()
        ic(date)
        date += relativedelta(months=1)
        ic(date.strftime("%Y-%m-%d"))

        new_period = (
            None,
            period["id"],
            name,
            supplement_number,
            index_number,
            date.strftime("%Y-%m-%d"),
            comment,
            period["owner_id"],
            period["period_type_id"],
            None,
        )
        ic(new_period)
        inserted_id = db.go_insert(
            sql_sqlite_periods["insert_period"],
            new_period, message=f"вставлен новый период мониторинга {name}",
            )
        ic(inserted_id)
        return inserted_id


def delete_period_by_id(db_file: str, period_id: int):
    with SQLiteDB(db_file) as db:
        db.go_execute(sql_sqlite_periods["delete_period_by_id"], {"period_id": period_id})


def _get_supplement_period_id(db: SQLiteDB, supplement_number: int)-> int:
    """Получает id периода дополнения ТСН по его номеру. """
    result = db.go_select(
            sql_sqlite_periods["select_ton_supplement_by_supplement_number"],
            {"supplement_number": supplement_number},
        )
    if result is None:
        output_message_exit(f"не найден ТСН период дополнения", f" с номером {supplement_number}.")
    return result[0]['id']


def _get_index_period(db: SQLiteDB, index_number: int)-> sqlite3.Row | None:
    """Получает id индексного периода  ТСН по его номеру. """
    result = db.go_select(
            sql_sqlite_periods["select_ton_index_by_number"],
            {"index_number": index_number},
        )
    if result is None:
        output_message_exit(f"не найден ТСН индексный период", f" с номером {index_number}.")
    return result[0]




def create_new_ton_index_period(
    db_file: str, 
    supplement_number: int, 
    index_number: int, 
    own_name: str,
    larix_id: int,        
)->int:
    """Создание нового индексного периода ТСН. """
    with SQLiteDB(db_file) as db:
        parent_id = _get_supplement_period_id(db, supplement_number)
        previous_index = _get_index_period(db, index_number-1)
        previous_id = previous_index["id"]
        owner_id = previous_index["owner_id"]
        period_type_id = previous_index["period_type_id"]
        create_date = datetime.now().date()
        name = f"Индекс {index_number}/{supplement_number}" 
        new_period = (
            parent_id,
            previous_id,
            name,
            supplement_number,
            index_number,
            create_date.strftime("%Y-%m-%d"),
            own_name,
            owner_id,
            period_type_id,
            larix_id,
        )
        inserted_id = db.go_insert(
            sql_sqlite_periods["insert_period"],
            new_period, message=f"вставлен новый период мониторинга {name}",
            )
        ic(inserted_id)
        return inserted_id






if __name__ == "__main__":
    ic()
    db_name = DB_FILE

    # period_id = create_new_monitoring_period(
    #     db_name,
    #     previous_period="Апрель 2024",
    #     period_name="Мониторинг Май 2024 (212 сборник/дополнение 72)"
    # )
    # delete_period_by_id(db_name, 126) # period_id

    period_id = create_new_ton_index_period(
            DB_FILE,
            supplement_number=72, 
            index_number=212, 
            own_name = "Индекс Май 2024/Дополнение 72 (мониторинг Апрель)",
            larix_id=167597127,
            )