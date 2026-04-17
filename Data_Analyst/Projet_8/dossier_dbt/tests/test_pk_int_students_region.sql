SELECT
    region,
    year,
    COUNT(*)
FROM {{ ref('int_insee_region')}}
GROUP BY region, year
HAVING COUNT(*) > 1