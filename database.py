import sqlite3
import hashlib

def get_db():
    db = sqlite3.connect('users.db')
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    
    # Create users table with additional fields and specific IDs
    db.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        address TEXT
    )
    ''')
    
    # Insert default admin and user with different passwords and specific IDs
    admin_password = hashlib.md5('adminpass123'.encode()).hexdigest()
    user_password = hashlib.md5('userpass123'.encode()).hexdigest()
    
    try:
        db.execute('DELETE FROM users')  # Clear existing users
        db.execute(
            'INSERT INTO users (id, username, password, role, email, phone, address) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (1, 'admin', admin_password, 'admin', 'admin@company.com', '123-456-7890', '123 Admin Street, City, 12345')
        )
        db.execute(
            'INSERT INTO users (id, username, password, role, email, phone, address) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (2, 'user', user_password, 'user', 'user@company.com', '098-765-4321', '456 User Avenue, City, 54321')
        )
        db.commit()
    except sqlite3.IntegrityError:
        pass  # Users already exist
