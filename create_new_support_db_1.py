from icecream import ic
#
from config import DB_FILE
from DB_support import create_support_db

if __name__ == "__main__":
    db_name = DB_FILE
    ic(db_name)
    create_support_db(db_name)
