from parse_monitoring_src_file import monitoring_src_paths, load_monitoring_data_file
from config import DB_FILE

from DB_support import create_new_monitoring_period


if __name__ == "__main__":
    
    period_name = "Май 2024"
    src_data = monitoring_src_paths[period_name]
    #
    load_monitoring_data_file(
        period_name,
        src_data["monitoring_file"],
        src_data["sheet_name"],
        db_file=DB_FILE,
    )