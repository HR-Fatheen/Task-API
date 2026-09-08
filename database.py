import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg.connect(os.getenv("DATABASE_URL"))

def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks(
            id SERIAL PRIMARY KEY,
            title TEXT,
            done BOOLEAN
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM tasks")
    task_count = cursor.fetchone()[0]

    if task_count == 0:
        cursor.executemany("""
            INSERT INTO tasks (title, done)
            VALUES (%s, %s)
        """, [
            ("Learn Python", False),
            ("Test The Product", False),
            ("Configure The DB", False)
        ])

    connection.commit()
    cursor.close()
    connection.close()

initialize_database()
