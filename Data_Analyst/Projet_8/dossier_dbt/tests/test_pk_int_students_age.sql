SELECT
    age_group,
    year,
    COUNT(*)
FROM {{ ref('int_students_age')}}
GROUP BY age_group, year
HAVING COUNT(*) > 1