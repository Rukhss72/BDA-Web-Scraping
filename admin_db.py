# admin_db.py
import sqlite3
import hashlib

# Connect to SQLite DB
conn = sqlite3.connect("admin_users.db")
cursor = conn.cursor()

# Create admin table
cursor.execute("""
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
)
""")

# Create applications table
cursor.execute("""
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT,
    email TEXT,
    phone TEXT,
    user_location TEXT,
    job_title TEXT,
    company TEXT,
    cover_letter TEXT
)
""")

conn.commit()

# Add admin (one-time setup)
def add_admin(username, password):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    try:
        cursor.execute("INSERT INTO admins (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        print(" Admin added.")
    except sqlite3.IntegrityError:
        print(" Username already exists.")

# Run this only once to create an admin
add_admin("Ruk", "1234")

conn.close()
