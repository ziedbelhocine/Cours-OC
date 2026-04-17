{{ config(materialized='view') }}

with averages as (
    select
        year,
        round(avg(age_20_a_24ans)) as "20-24 ans",
        round(avg(age_25_a_29ans)) as "25-29 ans",
        round(avg(age_30_a_34ans)) as "30-34 ans",
        round(avg(age_35_a_39ans)) as "35-39 ans",
        round(avg(age_40_a_44ans)) as "40-44 ans",
        round(avg(age_45_a_49ans)) as "45-49 ans",
        round(avg(age_50_a_54ans)) as "50-54 ans",
        round(avg(age_55_a_59ans)) as "55-59 ans",
        round(avg(age_60_et_plus)) as "60 ans ou plus"
    from {{ ref("stg_insee") }}
    group by year
),

unpivoted as (
    select 
        year,
        age_group,
        population
    from averages
    unpivot (
        population for age_group in (
            "20-24 ans", "25-29 ans", "30-34 ans", "35-39 ans", 
            "40-44 ans", "45-49 ans", "50-54 ans", "55-59 ans", "60 ans ou plus"
        )
    )
)

select 
    year,
    age_group,
    population,
    round(
        100.0 * population / sum(population) over (partition by year),
        2
    ) as PCT_POPULATION_PER_YEAR
from unpivoted