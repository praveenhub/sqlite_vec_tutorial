"""
Step 1: Embed the .txt documents listed in /data and place these docs
with embeddings in the sqlite database.
"""

import sqlite3
from sqlite_vec import serialize_float32
import sqlite_vec
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

# Set up OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

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

# Create a table to store text files and their embeddings
db.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_name TEXT,
        content TEXT,
        embedding BLOB
    )
''')

# Function to get embeddings using OpenAI API
def get_openai_embedding(text):
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
            )
        return response.data[0].embedding    
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

# Iterate over .txt files in the /data directory
for file_name in os.listdir("data"):
    file_path = os.path.join("data", file_name)
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        # Generate embedding for the content
        embedding = get_openai_embedding(content)
        if embedding:
            # Insert file content and embedding into the database
            db.execute(
                'INSERT INTO documents (file_name, content, embedding) VALUES (?, ?, ?)',
                (file_name, content,serialize_float32(embedding))
            )

# Commit changes
db.commit()

# Verify data is loaded
for row in db.execute('SELECT id, file_name, content, vec_length(embedding) FROM documents'):
    print(row)
    break

# Close the database connection
db.close()
