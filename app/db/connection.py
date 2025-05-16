import os
import psycopg2
import psycopg2.extras

def get_connection():
    """Get a connection to the database using environment variables"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        dbname=os.getenv('DB_NAME', 'medspa'),
        user=os.getenv('DB_USER', 'medspa_user'),
        password=os.getenv('DB_PASSWORD', 'medspa_password'),
        cursor_factory=psycopg2.extras.DictCursor
    ) 