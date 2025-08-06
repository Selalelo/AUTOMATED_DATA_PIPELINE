# 📝 Naming Conventions

This document outlines the naming conventions used for schemas, tables, views, columns, and other objects in the data warehouse to ensure consistency, clarity, and maintainability.

---

## 📄 Table of Contents
- [General Principles](#general-principles)
- [Schema & Table Naming](#schema--table-naming)
- [Column Naming Conventions](#column-naming-conventions)
  - [Surrogate Keys](#surrogate-keys)
  - [Technical Columns](#technical-columns)
- [Stored Procedures](#stored-procedures)
- [✅ Summary](#-summary)

---

## 🧭 General Principles

✅ Names should be clear, concise, and readable  
✅ Use `snake_case` for naming  
✅ Prefix objects with the relevant schema name (e.g., `dev.`)  
✅ Avoid reserved keywords (e.g., `user`, `order`)  
✅ Maintain consistency across all layers of the data warehouse  

---

## 🗃️ Schema & Table Naming

### Schema: `dev`

- All models (staging, intermediate, and analytics-ready) reside in the `dev` schema.
- Tables/views should reflect their purpose using prefixes:
  - `stg_` for staging models
  - `fact_` for fact models (metrics, aggregates)
  - `dim_` for dimension models (categorical data)

### Examples:

```text
dev.stg_weather_data
dev.fact_weather_daily_summary
dev.fact_weather_hourly_summary
dev.dim_weather_condition