{{ config(materialized='view')}}

select
    replace(user_id, '-', '') as user_id,
    age_group,
    coalesce(gender, 'Unknown') as gender,
    region,
    year_path_started
from {{ source('openclassrooms', 'students')}}
where year_path_started <= year(current_date)
and year_path_started >= 2022