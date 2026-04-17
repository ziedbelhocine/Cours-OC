SELECT
    region,
    gender,
    year,
    COUNT(*)
FROM {{ ref('stg_insee') }}
GROUP BY region, gender, year
HAVING COUNT(*) > 1