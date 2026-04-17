{{ config(materialized='view') }}

select
    age_group,
    year_path_started as year,
    count(user_id) as total_students,
    round(
        100.0
        * count(user_id)
        / sum(count(user_id)) over (partition by year_path_started),
        2
    ) as pct_students_per_year
from {{ ref("stg_students") }}
group by age_group, year_path_started
order by count(user_id), year_path_started desc