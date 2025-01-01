from datetime import datetime
import sqlite3
import json
from werkzeug.security import generate_password_hash, check_password_hash

class Database:
    def __init__(self, db_path='game.db'):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_connection()
        c = conn.cursor()
        
        # Create users table with authentication fields
        c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            progress TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()

    def register_user(self, username, password, email):
        try:
            conn = self.get_connection()
            c = conn.cursor()
            
            # Hash the password before storing
            password_hash = generate_password_hash(password)
            initial_progress = json.dumps({'challenge1': False, 'challenge2': False, 'challenge3': False})
            
            c.execute('''
            INSERT INTO users (username, password_hash, email, progress)
            VALUES (?, ?, ?, ?)
            ''', (username, password_hash, email, initial_progress))
            
            conn.commit()
            conn.close()
            return True, "Registration successful"
        except sqlite3.IntegrityError as e:
            if "username" in str(e):
                return False, "Username already exists"
            elif "email" in str(e):
                return False, "Email already registered"
            return False, "Registration failed"

    def login_user(self, username, password):
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            return True, user['id']
        return False, "Invalid username or password"

    def get_user_progress(self, user_id):
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute('SELECT progress FROM users WHERE id = ?', (user_id,))
        result = c.fetchone()
        
        conn.close()
        
        if result:
            return json.loads(result['progress'])
        return {'challenge1': False, 'challenge2': False, 'challenge3': False}

    def save_user_progress(self, user_id, progress):
        conn = self.get_connection()
        c = conn.cursor()
        
        progress_json = json.dumps(progress)
        c.execute('''
        UPDATE users 
        SET progress = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (progress_json, user_id))
        
        conn.commit()
        conn.close()

    def get_user_by_id(self, user_id):
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute('SELECT username, email FROM users WHERE id = ?', (user_id,))
        user = c.fetchone()
        
        conn.close()
        return dict(user) if user else None 