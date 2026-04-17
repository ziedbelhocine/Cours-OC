SELECT
    gender,
    year,
    COUNT(*)
FROM {{ ref('int_insee_gender')}}
GROUP BY gender, year
HAVING COUNT(*) > 1