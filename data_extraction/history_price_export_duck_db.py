
from psycopg2.extras import DictRow as pg_DictRow
import duckdb
import icecream as ic


from DB_support.sql_duck_db import sql_duck_db



def save_history_prices_support_duck_db(
    db_file: str, list_of_prices: list[pg_DictRow] = None
):
    """
    Сохранить список цен на материалы в  в DuckDB db_file.
    """
    with duckdb.connect(db_file) as con:
        con.sql(sql_duck_db["delete_table_material_prices"])
        con.sql(sql_duck_db["create_table_material_prices"])

        #
        results = con.sql(sql_duck_db["select_all_prices"]).fetchall()
        if results:
            ic(results)
        con.table("tblMaterialPrices").show()
        params = [
            [
                price["code"],
                price["base_price"],
                price["current_price"],
                price["index_number"],
            ]
            for price in list_of_prices
        ]
        print(params[:4])
        con.executemany(sql_duck_db["insert_row_material_prices"],
                params)
        con.table("tblMaterialPrices").show()
        con.sql(sql_duck_db["create_index_material_prices"])
        # for price in list_of_prices:
        #     # print(price)

        #     data = [
        #         price["code"],
        #         price["base_price"],
        #         price["current_price"],
        #         price["index_number"],
        #     ]

        #     # print(data)
        #     con.execute(
        #         sql_duck_db["insert_row_material_prices"],
        #         data,
        #     )
            # data = _prepare_material_data(material, period)
            # db.go_execute(sql_sqlite_materials["insert_row_expanded_material"], data)


#     con.executemany(
#         "INSERT INTO items VALUES (?, ?, ?)", [["chainsaw", 500, 10], ["iphone", 300, 2]]
# )



def show_pivot_table_duck_db(db_file: str):
    """
    Показать таблицу pivot в DuckDB db_file.
    """
    with duckdb.connect(db_file) as con:
        con.sql("SELECT * FROM tblMaterialPrices LIMIT 10").show()
        con.sql("SELECT count(*) FROM tblMaterialPrices").show()
        con.sql("SELECT DISTINCT index_number FROM tblMaterialPrices").show()
        con.sql("SELECT count(DISTINCT index_number) FROM tblMaterialPrices").show()

        q = "PIVOT tblMaterialPrices ON index_number USING sum(current_price) GROUP BY code;"
        con.sql(q).show()

        q = "DROP TABLE IF EXISTS tblPivotPrice;"
        con.sql(q)

        q = """--sql
                CREATE TABLE tblPivotPrice AS
                    PIVOT tblMaterialPrices ON index_number
                    USING sum(current_price)
                    GROUP BY code;
            """
        con.sql(q)
        con.table("tblPivotPrice").show()


# COPY tbl TO 'output.parquet' (FORMAT PARQUET);
# COPY (SELECT * FROM tbl) TO 'output.csv' (HEADER, DELIMITER ',');
# COPY (SELECT * FROM tbl) TO 'output.parquet' (FORMAT PARQUET);