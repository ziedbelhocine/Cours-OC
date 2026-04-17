{{ config(materialized='view') }}

select 
    gender,
    year,
    sum(total) as total_population,
    round(
        100.0 * sum(total) / sum(sum(total)) over (partition by year), 
        2
    ) as pct_population_per_year
from {{ ref('stg_insee')}}
group by gender, year