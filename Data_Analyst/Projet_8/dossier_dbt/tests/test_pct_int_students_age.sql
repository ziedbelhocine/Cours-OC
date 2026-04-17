SELECT
    sum(pct_students_per_year) as pct
FROM {{ ref('int_students_age') }}
GROUP BY year
having pct > 100.5 and pct < 99.5