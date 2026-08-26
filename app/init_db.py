import sqlite3
import os
import secrets
from werkzeug.security import generate_password_hash

DATABASE = os.path.join(os.path.dirname(__file__), 'instance', 'users.db')

def init_db():
    # 确保 instance 目录存在
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # 创建表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            api_token TEXT,
            full_name TEXT,
            email TEXT,
            department TEXT
        )
    ''')
    # 插入管理员（如果不存在）
    admin = cursor.execute('SELECT * FROM users WHERE username = "admin"').fetchone()
    if not admin:
        token = secrets.token_hex(16)   # 32位十六进制随机字符串
        hashed = generate_password_hash('admin123')
        cursor.execute(
            '''INSERT INTO users (username, password, role, api_token, full_name, email, department)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            ('admin', hashed, 'admin', token, 'Administrator', 'admin@example.com', 'IT')
        )
        conn.commit()
        print(f"[+] Admin token generated: {token}")
    else:
        print("[+] Admin already exists, skipping insertion.")
    conn.close()