{{
    config(
        materialized = 'table',
        unique_key = 'id'
    )
}}

WITH source AS(
SELECT *
FROM {{ source('dev', 'raw_weather_data')}}
),

de_dup AS(
    SELECT
        *,
        ROW_NUMBER() OVER(PARTITION BY time ORDER BY time_inserted) as rn
    FROM source
)


SELECT 
    city,
    temperature,
    weather_description,
    wind_speed,
    time AS weather_time_local,
    (time_inserted + (utc_offset || 'hours')::interval) AS inserted_at_local
FROM de_dup
WHERE rn = 1
