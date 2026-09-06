import sqlite3

connection = sqlite3.connect("tasks.db")
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY,
        title TEXT,
        done BOOLEAN
    )
""")

connection.commit()

cursor.execute("SELECT COUNT (*) FROM tasks")
task_count = cursor.fetchone()[0]

if task_count == 0:
    cursor.executemany("""
    INSERT INTO tasks (title, done)
    VALUES (?, ?)
    """, [
        ("Learn Python", False),
        ("Test The Product", False),
        ("Configure The DB", False)
    ])

    connection.commit()