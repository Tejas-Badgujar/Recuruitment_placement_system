"""Centralized MySQL connection utility for RPMS."""
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load credentials from the project's .env file.
load_dotenv()


def get_connection():
    """Create and return a MySQL connection.

    Raises mysql.connector.Error if the server/database cannot be reached.
    """
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "recruitment_placement_db"),
        connection_timeout=5,
    )


def test_connection():
    """Check the connection and print the selected database."""
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE(), VERSION()")
        database_name, server_version = cursor.fetchone()
        print("Database connection successful.")
        print(f"Database: {database_name}")
        print(f"MySQL/MariaDB version: {server_version}")
        cursor.close()
        return True
    except Error as error:
        print("Database connection failed.")
        print(f"Reason: {error}")
        return False
    finally:
        if connection is not None and connection.is_connected():
            connection.close()
