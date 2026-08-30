import os
import secrets
from flask import Flask, render_template, request, redirect, url_for, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from database import (
    get_db_connection,
    get_user_by_id,
    get_user_by_username,
    get_user_by_internal_id,
    create_user,
    update_user,
    get_admin_token
)
from init_db import init_db

app = Flask(__name__)

# SECRET_KEY 强制从环境变量读取
secret_key = os.environ.get("SECRET_KEY")
if not secret_key:
    raise RuntimeError("SECRET_KEY environment variable must be set")
app.secret_key = secret_key

FLAG = os.environ.get('FLAG', 'flag{test_flag}')

# ---------- 辅助函数 ----------
def login_required():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return None

def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        user = get_user_by_id(user_id)
        if user is None:
            session.clear()
        return user
    return None

# ---------- 路由 ----------
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        department = request.form.get('department')
        if not username or not password:
            return "用户名和密码不能为空", 400
        if get_user_by_username(username):
            return "用户名已存在", 400
        hashed = generate_password_hash(password)
        create_user(username, hashed, full_name, email, department)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = get_user_by_username(username)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        return "用户名或密码错误", 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    login_redirect = login_required()
    if login_redirect:
        return login_redirect
    user = get_current_user()
    if user is None:
        session.clear()
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=user)

@app.route('/profile/<int:user_id>')
def profile(user_id):
    login_redirect = login_required()
    if login_redirect:
        return login_redirect
    target = get_user_by_id(user_id)
    if not target:
        abort(404)
    # 漏洞点：未检查当前用户是否有权查看该 user_id
    return render_template('profile.html', user=target)

@app.route('/profile/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_profile(user_id):
    login_redirect = login_required()
    if login_redirect:
        return login_redirect
    if session['user_id'] != user_id:
        abort(403)
    user = get_current_user()
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        department = request.form.get('department')
        update_user(user_id, full_name=full_name, email=email, department=department)
        return redirect(url_for('profile', user_id=user_id))
    return render_template('edit_profile.html', user=user)

@app.route('/api/token', methods=['GET'])
def get_token():
    if 'user_id' not in session:
        return {"error": "未登录"}, 401
    
    uid = request.args.get('uid')
    if not uid:
        return {"error": "缺少 uid 参数"}, 400
    
    user = get_user_by_internal_id(uid)
    if not user:
        return {"error": "无效的员工编号"}, 404
    
    # 漏洞点：未检查当前用户是否有权获取该 uid 对应的 token
    # 任何登录用户都可以请求任意 internal_id 的 token
    return {
        "uid": user['internal_id'],
        "username": user['username'],
        "api_token": user['api_token'] if user['api_token'] else None
    }

@app.route('/admin', methods=['GET'])
def admin_panel():
    login_redirect = login_required()
    if login_redirect:
        return login_redirect
    token = request.headers.get('X-Admin-Token')
    if not token:
        abort(403)
    admin_token = get_admin_token()
    if token == admin_token:
        return render_template('admin.html', flag=FLAG)
    abort(403)

# ---------- 初始化 ----------
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)