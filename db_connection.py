from flask import Flask
import mysql.connector

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "admin",
    "database": "v_school"
}

def data_connection():
    try:
        db_connection = mysql.connector.connect(**db_config)
        print('Database is connected')
        return db_connection  # Return the connection object
    except mysql.connector.Error as dberr:
        print('Database is not connected', dberr)
        return None  # Return None on connection failure

if __name__ == '__main__':
    db_connect = data_connection()
    if db_connect is not None:
        db_connect.close()
