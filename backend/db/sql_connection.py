import mysql.connector
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

def get_sql_connection():

    # Validate required variables
    if not os.getenv("MYSQL_USER"):
        raise ValueError("Missing MYSQL_USER in .env file")

    if not os.getenv("MYSQL_PASSWORD"):
        raise ValueError("Missing MYSQL_PASSWORD in .env file")

    if not os.getenv("MYSQL_DB"):
        raise ValueError("Missing MYSQL_DB in .env file")

    # Create connection 
    return mysql.connector.connect(
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        database=os.getenv("MYSQL_DB"),
        autocommit=True
    )
