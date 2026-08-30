# CTF 题目：员工信息管理系统（IDOR）

这是一个为 GZCTF 平台设计的入门级 Web CTF 题目，核心漏洞为 IDOR（不安全的直接对象引用），对应 OWASP Top 10 2021 A01：访问控制失效。

## 项目结构

```text
CTF-WEB-IDOR/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── Writeup.md
└── app/
    ├── app.py
    ├── database.py
    ├── init_db.py
    ├── static/
    │   └── style.css
    └── templates/
        ├── base.html
        ├── login.html
        ├── register.html
        ├── dashboard.html
        ├── profile.html
        ├── edit_profile.html
        └── admin.html
```

## 快速构建与运行

### 使用 Docker

```bash
# 构建镜像
docker build -t eis .

# 运行容器（指定 Flag）
docker run -d --name eis -p 5000:5000 -e "FLAG=flag{your_flag_here}" eis

# 查看日志
docker logs eis

# 停止并删除
docker stop eis 
docker rm eis
```
使用 docker-compose
```bash
docker-compose up --build -d
docker-compose down
```
## 环境变量

|变量名|说明|是否必须|
|---|---|---|
|FLAG|最终要获得的 Flag 字符串|否（默认 flag{test_flag}）|
|SECRET_KEY|Flask Session 加密密钥|**是（必须设置）**|

**重要**：`SECRET_KEY` 必须通过环境变量显式设置，否则应用启动时会报错并退出。部署到 GZCTF 时，请确保平台为该 Challenge 注入 `SECRET_KEY` 环境变量。

## 题目逻辑概要

普通用户注册登录后可查看 /profile/<id> 和编辑自己的资料。

系统为每个用户分配一个员工编号（如 user-002）。

通过观察 URL 中的数字 ID，可尝试访问 /profile/1 获取管理员资料。

管理员资料中包含员工编号 admin-001 和职位信息。

仪表板中提供“API 令牌管理”功能，用于获取当前用户的 API 令牌。

该功能向 /api/token?uid=<员工编号> 发起请求，但未校验请求者是否有权获取指定员工编号的令牌。

将 uid 参数改为 admin-001 可获取管理员的 API 令牌。

使用该令牌作为请求头 X-Admin-Token 访问 /admin 即可获得 Flag。

## 部署到 GZCTF

将整个项目打包或上传至 GZCTF 的 Challenge 配置。

平台会自动构建镜像并运行，注入 FLAG 环境变量。

容器内服务监听 5000/tcp，由 GZCTF 映射对外端口。

无需特殊权限。

## 注意事项

本题目仅供学习与授权测试使用。

请勿在未授权环境中部署或利用。

如需修改管理员初始 token 生成逻辑，可调整 init_db.py 中的 secrets.token_hex(16)。