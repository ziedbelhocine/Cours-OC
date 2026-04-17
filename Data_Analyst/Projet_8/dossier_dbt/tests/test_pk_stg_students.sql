select
    user_id,
    year_path_started,
    count(*) as nb_rows
from {{ ref('stg_students') }}
group by user_id, year_path_started
having count(*) > 1