SELECT
    sum(delta_pct) as pct
FROM {{ ref('marts_region') }}
GROUP BY year
having pct > 100 and pct < -100