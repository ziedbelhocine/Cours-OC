{{ config(materialized='table') }}

select
    s.year,
    s.region,
    s.PCT_STUDENTS_PER_YEAR - i.PCT_POPULATION_PER_YEAR as delta_pct
from {{ ref('int_students_region')}} as s
left join {{ ref('int_insee_region')}}  as i on s.year = i.year and s.region = i.region