{{
  config(materialized='table')
}}

SELECT
  weather_description,
  COUNT(*) AS frequency
FROM {{ ref('staging') }}
GROUP BY weather_description
ORDER BY frequency DESC
