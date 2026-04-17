SELECT
    year,
    region,
    COUNT(*)
FROM {{ ref('marts_region') }}
GROUP BY year, region
HAVING COUNT(*) > 1