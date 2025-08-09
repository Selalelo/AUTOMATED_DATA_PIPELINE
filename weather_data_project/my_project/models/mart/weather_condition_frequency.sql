{{
  config(materialized='table')
}}

SELECT
  LOWEWER(weather_description),
  COUNT(*) AS frequency
FROM {{ ref('staging') }}
GROUP BY weather_description
ORDER BY frequency DESC