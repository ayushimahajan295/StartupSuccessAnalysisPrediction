import sqlite3
import os
import hashlib

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Create directory for database if it doesn't exist
os.makedirs('data', exist_ok=True)

# Create database and tables
conn = sqlite3.connect('data/startup.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    action TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    funding INTEGER,
    accelerator INTEGER,
    revenue INTEGER,
    prediction TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# Add sample users with hashed passwords
admin_pwd = hash_password('admin123')
user_pwd = hash_password('user123')

c.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin', ?, 'admin')", (admin_pwd,))
c.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('user', ?, 'user')", (user_pwd,))

conn.commit()
print("Database initialized successfully with sample users:")
print("- Admin: username='admin', password='admin123'")
print("- User: username='user', password='user123'")
conn.close()