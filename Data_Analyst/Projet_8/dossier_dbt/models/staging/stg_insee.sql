{{ config(materialized='view')}}

with cleaned_data as (
    select
        case 
            when Regions in ('Mayotte', 'Martinique', 'Guadeloupe', 'La Réunion', 'Guyane', 'DOM') then 'DROM'
            when Regions = 'Centre-Val-de-Loire' then 'Centre-Val de Loire'
            else Regions 
        end as region,
        Genre as gender,
        Annee as year,
        try_to_number(replace("20 a 24 ans", ' ', '')) as age_20_a_24ans,
        try_to_number(replace("25 a 29 ans", ' ', '')) as age_25_a_29ans,
        try_to_number(replace("30 a 34 ans", ' ', '')) as age_30_a_34ans,
        try_to_number(replace("35 a 39 ans", ' ', '')) as age_35_a_39ans,
        try_to_number(replace("40 a 44 ans", ' ', '')) as age_40_a_44ans,
        try_to_number(replace("45 a 49 ans", ' ', '')) as age_45_a_49ans,
        try_to_number(replace("50 a 54 ans", ' ', '')) as age_50_a_54ans,
        try_to_number(replace("55 a 59 ans", ' ', '')) as age_55_a_59ans,
        try_to_number(replace("60 a 64 ans", ' ', '')) + try_to_number(replace("65 a 69 ans", ' ', '')) as age_60_et_plus
    from {{ source('openclassrooms', 'INSEE')}}
)

select
    region,
    gender,
    year,
    sum(age_20_a_24ans) as age_20_a_24ans,
    sum(age_25_a_29ans) as age_25_a_29ans,
    sum(age_30_a_34ans) as age_30_a_34ans,
    sum(age_35_a_39ans) as age_35_a_39ans,
    sum(age_40_a_44ans) as age_40_a_44ans,
    sum(age_45_a_49ans) as age_45_a_49ans,
    sum(age_50_a_54ans) as age_50_a_54ans,
    sum(age_55_a_59ans) as age_55_a_59ans,
    sum(age_60_et_plus) as age_60_et_plus,
    (sum(age_20_a_24ans) + sum(age_25_a_29ans) + sum(age_30_a_34ans) + 
        sum(age_35_a_39ans) + sum(age_40_a_44ans) + sum(age_45_a_49ans) + 
        sum(age_50_a_54ans) + sum(age_55_a_59ans) + sum(age_60_et_plus)
    ) as total
from cleaned_data
group by 1, 2, 3
