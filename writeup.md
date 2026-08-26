
---

## 📄 Writeup.md（完整题解）

```markdown
# Writeup: Employee Information System (IDOR)

## 题目信息

- **名称**：Employee Information System
- **类型**：Web
- **难度**：入门 / Easy
- **考点**：IDOR, HTTP Headers, Cookie/Session, Burp Suite 基础
- **目标**：获取管理员面板中的 Flag

---

## 攻击步骤

### 1. 注册普通用户并登录

访问题目首页，点击注册，填写用户名、密码及其他信息，完成注册。  
登录后进入仪表板，页面显示当前用户信息。

### 2. 观察正常功能并发现可疑 URL

在仪表板中点击“My Profile”，浏览器跳转到类似 `/profile/2` 的地址（数字为当前用户的 ID）。  
注意到 URL 中包含可变的数字参数，猜想可能可以通过修改 ID 查看其他用户资料。

### 3. 尝试越权访问管理员资料

将 URL 中的 ID 改为 `1`（通常为第一个用户，即管理员），访问 `/profile/1`。  
页面成功加载，显示管理员（`admin`）的详细信息，其中包含一个字段：

API Token: e09abff3dbbd3bd4e4b6a67fc9398339

这说明后端没有校验当前用户是否有权访问该资源，存在 IDOR 漏洞。

### 4. 获取管理员 Token

直接从页面复制该 Token，或通过 Burp Suite 拦截响应后提取。

### 5. 利用 Token 访问管理员面板

管理员面板位于 `/admin`，但需要通过请求头 `X-Admin-Token` 传递正确的 Token 才能访问。

- 使用 Burp Repeater，构造如下请求：

```
GET /admin HTTP/1.1
Host: 127.0.0.1:5000
Cookie: session=eyJlc2VvX2lkIjoyfQ.a07lqq.THGda79Fj-2PaQGKR4fWIITXcFw
X-Admin-Token: e09abff3dbbd3bd4e4b6a67fc9398339
Connection: close
```

- 发送请求后，响应中包含：

```html
<h2>Admin Panel</h2>
<p>Congratulations! The flag is: <strong>flag{test_flag}</strong></p>
```