
{{
  config(
    materialized = 'table'
  )
}}

WITH weather AS (
  SELECT *
  FROM {{ ref('staging') }}
),

daily_summary AS (
  SELECT
    date_trunc('day', weather_time_local) AS date,
    COUNT(*) AS observations,
    ROUND(AVG(temperature)::NUMERIC, 2) AS avg_temp,
    ROUND(MIN(temperature)::NUMERIC, 2) AS min_temp,
    ROUND(MAX(temperature)::NUMERIC, 2) AS max_temp,
    ROUND(AVG(wind_speed::FLOAT)::NUMERIC, 2) AS avg_wind_speed
  FROM weather
  GROUP BY date
)

SELECT * FROM daily_summary
