import sqlite3
import os

DATABASE = os.path.join(os.path.dirname(__file__), 'instance', 'users.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user

def get_user_by_username(username):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

def get_user_by_internal_id(internal_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE internal_id = ?', (internal_id,)).fetchone()
    conn.close()
    return user

def create_user(username, password_hash, full_name, email, department):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO users (username, password, full_name, email, department, role)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (username, password_hash, full_name, email, department, 'user')
    )
    user_id = cursor.lastrowid
    internal_id = f"user-{str(user_id).zfill(3)}"
    cursor.execute(
        'UPDATE users SET internal_id = ? WHERE id = ?',
        (internal_id, user_id)
    )
    conn.commit()
    conn.close()

def update_user(user_id, full_name=None, email=None, department=None):
    conn = get_db_connection()
    if full_name is not None:
        conn.execute('UPDATE users SET full_name = ? WHERE id = ?', (full_name, user_id))
    if email is not None:
        conn.execute('UPDATE users SET email = ? WHERE id = ?', (email, user_id))
    if department is not None:
        conn.execute('UPDATE users SET department = ? WHERE id = ?', (department, user_id))
    conn.commit()
    conn.close()

def get_admin_token():
    conn = get_db_connection()
    row = conn.execute('SELECT api_token FROM users WHERE role = "admin" LIMIT 1').fetchone()
    conn.close()
    return row['api_token'] if row else None