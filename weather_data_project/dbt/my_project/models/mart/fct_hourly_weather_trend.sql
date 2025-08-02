{{
  config(
    materialized = 'table'
  )
}}

SELECT
  date_trunc('hour', weather_time_local) AS hour,
  ROUND(AVG(temperature)::NUMERIC, 2) AS avg_temp,
  ROUND(AVG(wind_speed::FLOAT)::NUMERIC, 2) AS avg_wind
FROM {{ ref('staging') }}
GROUP BY hour
ORDER BY hour
