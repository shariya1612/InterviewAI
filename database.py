import sqlite3
import os
from datetime import datetime


# ============================================================
# DATABASE LOCATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = os.path.join(
    BASE_DIR,
    "interview.db"
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    # Enable foreign key support
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

def create_tables():

    connection = get_connection()

    cursor = connection.cursor()


    # ========================================================
    # USERS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            created_at TEXT NOT NULL

        )
    """)


    # ========================================================
    # INTERVIEWS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interviews (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            role TEXT NOT NULL,

            interview_type TEXT NOT NULL,

            score REAL DEFAULT 0,

            date TEXT NOT NULL,

            question TEXT,

            answer TEXT,

            feedback TEXT,

            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE

        )
    """)


    connection.commit()

    connection.close()

    print("Database tables created successfully.")


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    create_tables()

    print(
        f"Database created at:\n{DATABASE}"
    )