SELECT
    age_group,
    year,
    COUNT(*)
FROM {{ ref('marts_age') }}
GROUP BY age_group, year
HAVING COUNT(*) > 1