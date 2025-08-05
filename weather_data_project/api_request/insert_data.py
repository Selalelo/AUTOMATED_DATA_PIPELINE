import psycopg2
from .api_request import fetch_weather
from datetime import datetime, timedelta, timezone
import os
#from dotenv import load_dotenv

# load_dotenv()

DB_HOST = os.getenv("DB_HOST")
PORT = os.getenv("PORT", 5432)  # Default to 5432 if not set
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_USER = os.getenv("DB_USER")
DB_NAME = os.getenv("DB_NAME")
def connect_db():
    print("Connecting to database...")
    try:
        conn = psycopg2.connect(
            host= DB_HOST,
            user= DB_USER,
            port= PORT,
            dbname= DB_NAME,
            password= DB_PASSWORD
        )
        print("Connection successful")
        return conn
    except psycopg2.Error as e:
        print(f'Database connection failed: {e}')
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
                time_inserted TIMESTAMP DEFAULT NOW(),
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
    temp_celsius = (data["main"]["temp"] - 32) * 5.0/9.0  # Convert Fahrenheit to Celsius
    try:
        cursor = conn.cursor()

        # Create timezone-aware UTC datetime
        utc_time = datetime.fromtimestamp(data["dt"], tz=timezone.utc) 

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
            ) VALUES (%s, %s, %s, %s, %s, NOW(), %s)
            """, (
                data["name"],
                temp_celsius,
                data["weather"][0]["description"],
                str(data["wind"]["speed"]),
                utc_time, 
                str(data["timezone"]/3600) 
            )
        )
        conn.commit()
        print("Data inserted.")
    except psycopg2.Error as e:
        print(f'Failed to insert data into the database: {e}')
        raise



def main():
    city = 'Johannesburg'
    conn = None  # Initialize conn variable
    try:
        data = fetch_weather(city)
        conn = connect_db()
        create_table(conn)
        insert_records(conn, data)
    except Exception as e:
        print(f'An error occurred during execution: {e}')
    finally:
        if conn is not None:  # Better way to check if conn exists
            conn.close()
            print('Database connection closed')

main() 
