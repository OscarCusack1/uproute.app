import sqlite3

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Drop the users table if it exists
cursor.execute("DROP TABLE IF EXISTS users;")

# SQL script to create the users table
sql_script = """
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    api_key TEXT NOT NULL UNIQUE
);
"""

# Execute the SQL script
cursor.executescript(sql_script)

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database and table created successfully.")