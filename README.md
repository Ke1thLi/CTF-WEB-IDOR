# CTF Challenge: Employee Information System (IDOR)

这是一个为 GZCTF 平台设计的入门级 Web CTF 题目，核心漏洞为 IDOR（不安全的直接对象引用），对应 OWASP Top 10 2021 A01: Broken Access Control。

## 项目结构
.
├── Dockerfile
├── docker-compose.yml（可选）
├── requirements.txt
├── README.md
└── app/
├── app.py
├── database.py
├── init_db.py
├── static/
│ └── style.css
└── templates/
├── base.html
├── login.html
├── register.html
├── dashboard.html
├── profile.html
├── edit_profile.html
└── admin.html

text

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
docker stop eis && docker rm eis
使用 docker-compose
bash
docker-compose up --build -d
docker-compose down
环境变量
变量名	说明	默认值
FLAG	最终要获得的 Flag 字符串	flag{test_flag}
SECRET_KEY	Flask session 加密密钥	固定值（建议生产环境修改）
数据库（SQLite）会在容器首次启动时自动初始化，并创建管理员账户：

用户名：admin

密码：admin123（哈希存储，但攻击过程中不需要）

同时会生成一个随机的 api_token（32 位十六进制）

题目逻辑概要
普通用户注册登录后可查看 /profile/<id> 和编辑自己的资料。

管理员账户预置，普通用户可通过 IDOR 访问 /profile/1 获取管理员的 api_token。

使用该 token 作为请求头 X-Admin-Token 访问 /admin 即可获得 Flag。

部署到 GZCTF
将整个项目打包或上传至 GZCTF 的 Challenge 配置。

平台会自动构建镜像并运行，注入 FLAG 环境变量。

容器内服务监听 5000/tcp，由 GZCTF 映射对外端口。

无需特殊权限。

注意事项
本题目仅供学习与授权测试使用。

请勿在未授权环境中部署或利用。

如需修改管理员初始 token 生成逻辑，可调整 init_db.py 中的 secrets.token_hex(16)。