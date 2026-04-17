SELECT
    gender,
    year,
    COUNT(*)
FROM {{ ref('marts_gender') }}
GROUP BY gender, year
HAVING COUNT(*) > 1