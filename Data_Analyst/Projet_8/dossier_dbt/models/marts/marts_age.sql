{{ config(materialized='table') }}

select
    s.year,
    s.age_group,
    s.PCT_STUDENTS_PER_YEAR - i.PCT_POPULATION_PER_YEAR as delta_pct
from {{ ref('int_students_age')}} as s
left join {{ ref('int_insee_age')}}  as i on s.year = i.year and s.age_group = i.age_group