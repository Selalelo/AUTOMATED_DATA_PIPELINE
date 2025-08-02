import psycopg2
from api_request import fetch_weather
from datetime import datetime, timedelta, timezone

def connect_db():
    print("Connecting to database...")
    try:
        conn = psycopg2.connect(
            host='localhost',
            user='user',
            port=5432,
            dbname='mydatabase',
            password='password'
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
                data["main"]["temp"],
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
    try:
        data = fetch_weather(city)
        conn = connect_db()
        create_table(conn)
        insert_records(conn, data)
    except Exception as e:
        print(f'An error occured during execution: {e}')
    finally:
        if conn in locals():
            conn.close()
            print('Database connection closed')

main() 
