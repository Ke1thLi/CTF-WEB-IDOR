import sqlite3
import os
import secrets
from werkzeug.security import generate_password_hash

DATABASE = os.path.join(os.path.dirname(__file__), 'instance', 'users.db')

def init_db():
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            api_token TEXT,
            internal_id TEXT,
            full_name TEXT,
            email TEXT,
            department TEXT
        )
    ''')
    
    admin = cursor.execute('SELECT * FROM users WHERE username = "admin"').fetchone()
    if not admin:
        token = secrets.token_hex(16)
        hashed = generate_password_hash('Adm1n@EIS#2026_Secure')
        cursor.execute(
            '''INSERT INTO users 
               (username, password, role, api_token, internal_id, full_name, email, department)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            ('admin', hashed, 'admin', token, 'admin-001', '系统管理员', 'admin@company.com', '技术部')
        )
        conn.commit()
        print("[+] Admin created with internal_id: admin-001")
        print("[+] API Token: " + token + " (可通过 API 获取)")
    conn.close()