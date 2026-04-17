SELECT
    age_group,
    year,
    COUNT(*)
FROM {{ ref('int_insee_age') }}
GROUP BY age_group year
HAVING COUNT(*) > 1