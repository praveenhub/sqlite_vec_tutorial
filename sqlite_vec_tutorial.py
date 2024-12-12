"""
A tutorial on how to use SQLite-vec for retrieval augmented generation
"""

import sqlite3
import sqlite_vec
import os

# Path to the database file
db_path = 'my_docs.db'

# Delete the database file if it exists
if os.path.exists(db_path):
    os.remove(db_path)

# Connect to a database (or create it if it doesn't exist)
db = sqlite3.connect(db_path)
db.enable_load_extension(True)
sqlite_vec.load(db)
db.enable_load_extension(False)

# Checking version of sqlite-vec
vec_version, = db.execute("select vec_version()").fetchone()
print(f"vec_version={vec_version}")

# Create a table to store text files
db.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_name TEXT,
        content TEXT
    )
''')

# Iterate over .txt files in the /data directory
for file_name in os.listdir("data"):
    file_path = os.path.join("data", file_name)
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        # Insert file content into the database
        db.execute('INSERT INTO documents (file_name, content) VALUES (?, ?)', (file_name, content))

# Commit changes
db.commit()

# Verify data is loaded
for row in db.execute('SELECT * FROM documents'):
    print(row)
