SELECT
    year,
    sum(pct) as sum_pct
FROM {{ ref('marts_gender') }}
GROUP BY year, gender 
having sum_pct > 100.5 and sum_pct < 99.5