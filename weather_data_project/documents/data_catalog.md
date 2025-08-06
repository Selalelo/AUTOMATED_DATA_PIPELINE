# 📒 Data Catalogue: dev Schema

This document describes the data models in the **`dev`** schema, forming the presentation layer for analytics and reporting in the weather data pipeline.

---

## ⭐ `dev.fact_weather_daily_summary`

**Description:**  
Summarized daily weather metrics including average, minimum, and maximum temperatures, as well as average wind speed.

| Column         | Data Type | Description                                      |
|----------------|-----------|--------------------------------------------------|
| date           | DATE      | Truncated local weather time (day-level)         |
| observations   | INT       | Number of weather records for that day          |
| avg_temp       | FLOAT     | Average temperature (°C)                         |
| min_temp       | FLOAT     | Minimum temperature (°C)                         |
| max_temp       | FLOAT     | Maximum temperature (°C)                         |
| avg_wind_speed | FLOAT     | Average wind speed (m/s)                        |

---

## ⭐ `dev.fact_weather_hourly_summary`

**Description:**  
Hourly aggregated weather facts for temperature and wind analysis.

| Column     | Data Type | Description                           |
|------------|-----------|---------------------------------------|
| hour       | TIMESTAMP | Weather timestamp truncated to hour   |
| avg_temp   | FLOAT     | Average temperature per hour (°C)     |
| avg_wind   | FLOAT     | Average wind speed per hour (m/s)    |

---

## ⭐ `dev.dim_weather_condition`

**Description:**  
Dimension table representing the frequency of unique weather conditions observed.

| Column             | Data Type | Description                                  |
|--------------------|-----------|----------------------------------------------|
| weather_description| TEXT      | Description of the weather (e.g., clear sky) |
| frequency          | INT       | Number of times this condition was recorded  |

---

## ⭐ `dev.stg_weather_data`

**Description:**  
Cleaned staging table from the raw weather data source, including deduplicated entries and localized timestamps.

| Column            | Data Type | Description                                              |
|-------------------|-----------|----------------------------------------------------------|
| city              | TEXT      | Name of the city                                         |
| temperature       | FLOAT     | Temperature recorded (°C)                                |
| weather_description | TEXT    | Textual weather description                              |
| wind_speed        | TEXT      | Wind speed in m/s (raw form)                            |
| weather_time_local| TIMESTAMP | Original time from API                                   |
| inserted_at_local | TIMESTAMP | Local insertion time based on UTC offset                |

---

## 🧾 Notes

- All models reside in the `dev` schema and follow a star schema convention.
- `fact_` prefix indicates fact tables with measurable metrics.
- `dim_` prefix is used for descriptive or categorical data.
- `stg_` prefix denotes staging models prepared from raw sources.
- Timestamps are converted to local time using the `utc_offset` column logic.
