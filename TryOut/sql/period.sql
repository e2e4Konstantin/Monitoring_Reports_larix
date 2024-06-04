SELECT id, description FROM tblDirectories WHERE directory='owners' AND name='TON';

WITH 
    own(id, description) AS (
    SELECT id, description FROM tblDirectories WHERE directory='owners' AND name='TON'
    ),
    type(id, description) AS (
    SELECT id, description FROM tblDirectories WHERE directory='period_types' AND name='supplement'
    )
SELECT * 
FROM tblPeriods   
WHERE 
    owner_id = (select id from own)
    and
    period_type_id = (select id from type)
    ;    

WITH
    owner(id) AS (
        SELECT id FROM tblDirectories WHERE directory = 'owners' AND name = 'TON'
    ),
    period_type(id) AS (
        SELECT id FROM tblDirectories WHERE directory = 'period_types' AND name = 'supplement'
    )
SELECT *
FROM tblPeriods
WHERE
    owner_id = owner.id
    AND period_type_id = period_type.id;
    


WITH
    owner_row AS (
        SELECT id FROM tblDirectories WHERE directory='owners' AND name='TON'
    ),
    period_type_row AS (
        SELECT id FROM tblDirectories WHERE directory='period_types' AND name='supplement'
    )
SELECT *
FROM tblPeriods
WHERE
    owner_id = (SELECT id FROM owner_row)
    AND period_type_id = (SELECT id FROM period_type_row)
ORDER BY supplement_number ASC    
;
    