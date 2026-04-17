{{ config(materialized='table') }}

select 
    concat(gender, '-students') as gender,
    year,
    pct_students_per_year as pct
from {{ ref('int_students_gender')}}
UNION ALL
select 
    concat(gender, '-insee') as gender,
    year,
    pct_population_per_year as pct
from {{ ref('int_insee_gender')}}