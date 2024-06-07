SELECT index_number r_id FROM tblPriceHistory;
SELECT index_number FROM tblPriceHistory GROUP BY index_number;

create table tblPriceHistory (pressmark, base_price, current_price, index_number);






select DISTINCT index_number from tblPriceHistory order by index_number;

create table tblRevers AS 
    pressmark TEXT,
    select DISTINCT index_number from tblPriceHistory order by index_number
;
ALTER TABLE tblRevers ADD COLUMN base_price REAL, ADD COLUMN current_price REAL; 

select 
    base_price, current_price, 
    index_number
from tblPriceHistory
where
    CAST(index_number as integer) = 204
;




with 
    idx as (
        select DISTINCT index_number from tblPriceHistory order by index_number
    ),
    ucode as (
        SELECT DISTINCT pressmark FROM tblPriceHistory 
    )
select 
    *,
    (SELECT base_price FROM tblPriceHistory WHERE pressmark = ucode.pressmark)
from ucode
;





CREATE TABLE tblExpandedMaterial (
    -- таблица для хранения развернутых Материалов для периодов
    -- развернутый: собранный из всех связанных таблиц
    id INTEGER PRIMARY KEY NOT NULL,
    --
    period_larix_id INTEGER,
    period_name TEXT,
    --
    product_type TEXT,
    code TEXT,
    digit_code INTEGER,
    description TEXT,
    unit_measure TEXT,
    -- 
    transport_code TEXT,
    transport_name TEXT,
    transport_base_price REAL,
    transport_current_price REAL,
    transport_inflation_rate REAL,
    -- 
    storage_cost_rate  REAL,
    storage_cost_name,
    storage_cost_description,
    -- 
    base_price REAL,
    current_price REAL,
    inflation_rate REAL
);






    
);

