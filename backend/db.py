# db.py
import mysql.connector
from config import db_config
import logging

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        logging.debug("Database connection established.")
        return conn
    except mysql.connector.Error as err:
        logging.error(f"Database connection error: {str(err)}")
        raise
