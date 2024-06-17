# Доработки
- добавить поле period_id в таблицу tblExpandedMaterial, ссылка на внутреннюю таблицу tblPeriods



# Отчет по данным мониторинга на основной БД PostgreSQL.
## Термины
ТСН - Территориальные сметные нормативы
ПСМ - Проектно сметный модуль
НЦКР - Нормативы цен на комплекс работ

TON: territorial outlay normative
PNWC: price normative for work complexes
POM: project outlay module

Материалы: Глава 1
Машины: Глава 2
Оборудование: Глава 13

Ресурсная модель расчета началась с 69 дополнения.



## Таблица для хранения периодов.

pip

pip install "pandas[excel]"