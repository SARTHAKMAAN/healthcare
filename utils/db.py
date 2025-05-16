import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Password@1",
        database="health_tracker"
    )
import mysql.connector

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='your_mysql_username',
            password='your_mysql_password',
            database='health_tracker'
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

