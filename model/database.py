import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DB_NAME = os.getenv('DB_NAME')

def initialize_database():
    # Connect to the database
    connection = sqlite3.connect(f'{DB_NAME}')
    cursor = connection.cursor()

    reminders = '''
        CREATE TABLE IF NOT EXISTS reminders ( 
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            task TEXT NOT NULL, 
            author_id INTEGER NOT NULL, 
            task_period TEXT NOT NULL, 
            task_trigger TEXT NOT NULL,
            server_id INTEGER NOT NULL,
            ch_id INTEGER NOT NULL,
            FOREIGN KEY (author_id) REFERENCES users (author_id)
        );'''

    # Create a table for storing user data
    cursor.execute(reminders)

    users = '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author_id INTEGER NOT NULL,
            name TEXT,
            global_name TEXT,
            UNIQUE(author_id)
        );'''

    cursor.execute(users)


    # Commit the changes and close the connection
    connection.commit()
    connection.close()