import psycopg2
from api_request import get_current_weather
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import os
import pytz

def get_db_connection_params():
    """Get database connection parameters from environment variables"""
    return {
        'host': os.getenv("DB_HOST"),
        'user': os.getenv("DB_USER"),
        'port': os.getenv("PORT", 5432),
        'dbname': os.getenv("DB_NAME"),
        'password': os.getenv("DB_PASSWORD"),
        'sslmode': os.getenv("POSTGRES_SSLMODE", "require")
    }

def connect_db():
    print("Connecting to database...")
    try:
        conn_params = get_db_connection_params()
        
        # Print connection info (without password)
        print(f"Connecting to: {conn_params['host']}:{conn_params['port']}")
        print(f"Database: {conn_params['dbname']}")
        print(f"User: {conn_params['user']}")
        
        # Check if required parameters are present
        if not all([conn_params['host'], conn_params['user'], conn_params['dbname'], conn_params['password']]):
            missing = [k for k, v in conn_params.items() if not v and k != 'sslmode']
            raise ValueError(f"Missing required database parameters: {missing}")
        
        conn = psycopg2.connect(**conn_params)
        print("Connection successful")
        return conn
    except psycopg2.Error as e:
        print(f'Database connection failed: {e}')
        raise
    except Exception as e:
        print(f'Error getting connection parameters: {e}')
        raise

def create_table(conn):
    print('Creating table if not exists...')
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE SCHEMA IF NOT EXISTS dev;

            CREATE TABLE IF NOT EXISTS dev.raw_weather_data (
                id SERIAL PRIMARY KEY,
                city TEXT,
                temperature FLOAT,
                weather_description TEXT,
                wind_speed TEXT,
                time TIMESTAMP,
                time_inserted TIMESTAMP,
                utc_offset TEXT
            );
            """
        )
        conn.commit()
        print("Table created (or already exists).")
    except psycopg2.Error as e:
        print(f'Failed to create table: {e}')
        raise

def insert_records(conn, data):
    print('Inserting data...')
    if not data:
        print("No data to insert")
        return
        
    try:
        cursor = conn.cursor()
        
        cursor.execute(
            """ 
            INSERT INTO dev.raw_weather_data(
                city,
                temperature,
                weather_description,
                wind_speed,
                time,
                time_inserted,
                utc_offset 
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                data["location"],
                data["temperature"],
                data["description"],
                str(data["wind_speed"]),
                data["timestamp"],
                data["timestamp"],
                data["utc_offset"]
            )
        )
        conn.commit()
        print(f"Data inserted successfully for {data['location']}")
    except psycopg2.Error as e:
        print(f'Failed to insert data into the database: {e}')
        raise
    except KeyError as e:
        print(f'Missing expected data field: {e}')
        print(f'Available data keys: {list(data.keys()) if data else "No data"}')
        raise

def add_time_info(data: dict, timezone_name="Africa/Johannesburg") -> dict:
    tz = pytz.timezone(timezone_name)
    now = datetime.now(tz)

    data["timestamp"] = now.isoformat()
    data["utc_offset"] = now.strftime("%z")  # e.g. "+0200"

    return data

def main():
    city = 'Johannesburg'
    conn = None
    try:
        print(f"Starting weather data pipeline for {city}")
        
        # Fetch weather data
        data = get_current_weather(city)
        if not data:
            print("Failed to fetch weather data, exiting")
            return
        
        data = add_time_info(data)

        # Connect to database
        conn = connect_db()
        
        # Create table if needed
        create_table(conn)
        
        # Insert data
        insert_records(conn, data)
        
        print("Weather data pipeline completed successfully")
        
    except Exception as e:
        print(f'An error occurred during execution: {e}')
        raise
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed')

if __name__ == "__main__":
    main()
