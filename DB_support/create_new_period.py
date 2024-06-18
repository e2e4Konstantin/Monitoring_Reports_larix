from datetime import datetime
from dateutil.relativedelta import relativedelta
from icecream import ic

from DB_support.db_config import SQLiteDB
from DB_support.sql_sqlite_periods import sql_sqlite_periods
from common_features import extract_monitoring_supplement_index_cmt
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


if __name__ == "__main__":
    ic()
    db_name = DB_FILE

    period_id = create_new_monitoring_period(
        db_name,
        previous_period="Апрель 2024",
        period_name="Мониторинг Май 2024 (212 сборник/дополнение 72)"
    )
    delete_period_by_id(db_name, 126) # period_id