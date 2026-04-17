SELECT
    sum(pct_population_per_year) as pct
FROM {{ ref('int_insee_age') }}
GROUP BY year
having pct > 100.5 and pct < 99.5