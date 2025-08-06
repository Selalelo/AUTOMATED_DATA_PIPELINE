# Weather Data Pipeline Project 🌦️🚀

Welcome to the **Weather Data Pipeline** repository!  
This project demonstrates an end-to-end modern data pipeline that ingests weather data from an external API, processes it into a data warehouse using dbt, and delivers clean, analysis-ready datasets. It’s designed as a portfolio project to showcase industry-standard practices in data engineering, automation, and analytics.

---

## 🚀 Project Requirements

### 🛠️ Building the Data Pipeline (Data Engineering)

**Objective:**

- **Data Source**  
  Pull real-time weather data from a public API.

- **Database Storage**  
  Insert raw data into a PostgreSQL database hosted on superbase.

- **Data Quality**  
  Clean and transform data using dbt (Data Build Tool).

- **Transformation**  
  Build marts directly from the `staging.sql` layer using dbt models:
  - Hourly Weather Metrics
  - Daily Weather Aggregates
  - Weather Descriptions

- **Automation**  
  Schedule data ingestion and transformation to run hourly via GitHub Actions.

- **Documentation**  
  Provide clear documentation for the pipeline, database models, and operational logic.

---

## ⚙️ Technologies Used

- **Python** – API requests, ETL logic  
- **PostgreSQL (superbase)** – Cloud-hosted database  
- **psycopg2** – DB connection and insertion  
- **dbt** – SQL-based transformation framework  
- **GitHub Actions** – CI/CD automation  
- **Streamlit** – Dashboarding/visualization frontend  

---

## 🗂️ Data Architecture

Below is the high-level data architecture for this project, showing the data flow from the live weather API source to the PostgreSQL database, through dbt transformations, and into the Streamlit dashboard for final consumption:


---
## 🚀 Live Demo

Click the image below to view the **live Streamlit dashboard**:

[![Weather Analytics Dashboard](https://raw.githubusercontent.com/your-username/weather_data_project/main/demo/demo_thumbnail.png)](https://automated-data-pipeline.streamlit.app/)


## 📁 Project File Structure
```plaintext
AUTOMATED_DATA_PIPELINE
|
├── .github                                               # GitHub Actions for CI/CD
│   └── workflows
│       └── main.yml                                      # Automation (fetch data, dbt runs, etc.)
├── weather_data_project
│   ├── api_request                                       # Python scripts to fetch & insert data
│   │   ├── __init__.py
│   │   ├── api_request.py
│   │   ├── insert_data.py
│   │   └── requirements.txt
│   ├── my_project                                        # dbt project folder
│   │   ├── models
│   │   │   ├── mart
│   │   │   │   ├── fct_daily_weather_summary.sql
│   │   │   │   ├── fct_hourly_weather_trend.sql
│   │   │   │   └── weather_condition_frequency.sql
│   │   │   ├── sources
│   │   │   │   └── sources.yml
│   │   │   └── staging
│   │   │       └── staging.sql
│   │   ├── README.md
│   │   └── dbt_project.yml                               
│   ├── streamlit_app                                     # Streamlit app
│   │   ├── .streamlit
│   │   │   └── config.toml
│   │   ├── app.py
│   │   └── requirements.txt
│   └── dbt_project.yml
├── LICENSE
└── readme.md
```
---
## 🛡️ License

This project is licensed under the **MIT License**. You are free to use, modify, and share this project with proper attribution.

---

## 🌟 About Me

Hi there! I’m **Selalelo Moakamelo**, and I’m passionate about data engineering and building modern data solutions. I love exploring how data can drive meaningful insights, and I’m always excited to keep learning, growing, and sharing knowledge along the way.

Let’s stay connected! Feel free to reach out and connect with me on:

- [LinkedIn](https://www.linkedin.com/in/selalelo-moakamelo-35b57719a)

---

*Thanks for exploring this project — happy data engineering!* 🚀
