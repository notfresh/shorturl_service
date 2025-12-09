# 快速开始指南

本指南将帮助你从零开始部署短网址服务项目，每一步都有详细说明。

## 前置要求

在开始之前，请确保你的系统已安装以下软件：

- **Python 3.6+** （推荐 Python 3.8+）
- **Git** （用于克隆代码）
- **pip** （Python 包管理器，通常随 Python 一起安装）

### 检查安装

**Windows (PowerShell/CMD):**
```powershell
python --version
git --version
pip --version
```

**Linux/Mac:**
```bash
python3 --version
git --version
pip3 --version
```

如果上述命令都能正常显示版本号，说明环境已就绪。如果未安装，请先安装相应的软件。

---

## 部署步骤

### 步骤 1: 克隆代码仓库

打开终端（Windows 使用 PowerShell 或 CMD，Linux/Mac 使用 Terminal），执行以下命令：

```bash
git clone https://github.com/notfresh/shorturl_service.git
```

或者如果你有 SSH 配置：

```bash
git clone git@github.com:notfresh/shorturl_service.git
```

克隆完成后，进入项目目录：

```bash
cd shorturl_service
```

---

### 步骤 2: 创建 Python 虚拟环境

虚拟环境可以隔离项目依赖，避免与其他项目冲突。

**Windows:**
```powershell
python -m venv venv
```

**Linux/Mac:**
```bash
python3 -m venv venv
```

如果遇到 `python: command not found` 错误，请使用 `python3` 替代 `python`。

---

### 步骤 3: 激活虚拟环境

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

如果遇到执行策略限制，先运行：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

激活成功后，命令行提示符前会显示 `(venv)` 标识。

---

### 步骤 4: 升级 pip

确保使用最新版本的 pip，避免依赖安装问题：

**Windows:**
```powershell
python -m pip install --upgrade pip
```

**Linux/Mac:**
```bash
python3 -m pip install --upgrade pip
```

或者直接使用虚拟环境中的 pip：

```bash
.\venv\Scripts\python.exe -m pip install --upgrade pip
```

---

### 步骤 5: 安装项目依赖

安装项目所需的所有 Python 包：

**Windows:**
```powershell
pip install -r requirements.txt
```

**Linux/Mac:**
```bash
pip install -r requirements.txt
```

**注意：** 如果安装过程中遇到编译错误（特别是 `mmh3` 包），这是因为缺少 C++ 编译工具。项目已更新 `requirements.txt` 使用预编译版本，通常不会遇到此问题。如果仍有问题，请参考错误提示安装相应的构建工具。

安装完成后，可以验证安装：

```bash
pip list
```

---

### 步骤 6: 配置环境变量

项目需要配置文件来设置数据库、Redis 等连接信息。

**Windows:**
```powershell
copy env\env.example.yml env\env.yml
```

**Linux/Mac:**
```bash
cp env/env.example.yml env/env.yml
```

然后编辑 `env/env.yml` 文件，根据你的实际情况修改配置：

```yaml
FLASK_ENV: development
COS_SECRET_ID:                    # 腾讯云 COS 密钥 ID（可选）
COS_SECERT_KEEY:                  # 腾讯云 COS 密钥（可选）
COS_REGION: ap-beijing            # 腾讯云 COS 区域（可选）
COS_BUCKET: zxzx                  # 腾讯云 COS 存储桶（可选）
COS_APPID:                        # 腾讯云 COS APPID（可选）
DOMAIN_NAME: localhost            # 域名，本地开发使用 localhost
PORT: 8000                        # 服务端口
HTTP: http                        # 协议，本地使用 http
REDIS_URL: redis://:@localhost:6379/0  # Redis 连接地址（可选，如果未安装 Redis 可留空）
FLASKY_MAIL_SUBJECT_PREFIX: ShortURL
ENVIRON: test                     # 环境标识
```

**重要说明：**
- 对于本地开发，大部分配置可以使用默认值
- 如果未安装 Redis，`REDIS_URL` 可以保持默认值（项目会尝试连接，但某些功能可能不可用）
- 如果使用 SQLite（默认），无需配置数据库连接
- 如果需要使用 MySQL，请在配置文件中添加 `SQLALCHEMY_DATABASE_URI` 或在环境变量中设置

---

### 步骤 7: 初始化数据库

项目使用 Flask-Migrate 管理数据库迁移。首次部署需要初始化数据库表结构。

**Windows:**
```powershell
python manage.py db upgrade
```

**Linux/Mac:**
```bash
python3 manage.py db upgrade
```

或者使用虚拟环境中的 Python：

```bash
.\venv\Scripts\python.exe manage.py db upgrade
```

**注意：** 
- 如果遇到迁移错误（特别是最后一个迁移），这是 SQLite 的 ALTER 约束限制导致的，不影响核心功能
- 数据库文件 `app.sqlite` 会在项目根目录自动创建
- 如果看到警告信息，可以忽略，只要没有致命错误即可

验证数据库是否创建成功：

**Windows:**
```powershell
python -c "from app import create_app; from app.db import db; from sqlalchemy import inspect; app = create_app('development'); app.app_context().push(); inspector = inspect(db.engine); print('已创建的表:', inspector.get_table_names())"
```

**Linux/Mac:**
```bash
python3 -c "from app import create_app; from app.db import db; from sqlalchemy import inspect; app = create_app('development'); app.app_context().push(); inspector = inspect(db.engine); print('已创建的表:', inspector.get_table_names())"
```

应该能看到 `['alembic_version', 'urls', 'users']` 三个表。

---

### 步骤 8: 创建测试用户（可选）

项目默认没有用户账户，你需要通过注册页面创建账户，或者通过命令行创建测试用户。

**通过命令行创建测试用户：**

**Windows:**
```powershell
python -c "from app import create_app; from app.db import db; from app.models import User; app = create_app('development'); app.app_context().push(); user = User(username='admin', email='admin@example.com', user_type=1, confirmed=True); user.password = 'admin123'; db.session.add(user); db.session.commit(); print('测试用户创建成功')"
```

**Linux/Mac:**
```bash
python3 -c "from app import create_app; from app.db import db; from app.models import User; app = create_app('development'); app.app_context().push(); user = User(username='admin', email='admin@example.com', user_type=1, confirmed=True); user.password = 'admin123'; db.session.add(user); db.session.commit(); print('测试用户创建成功')"
```

**测试用户信息：**
- 用户名: `admin`
- 邮箱: `admin@example.com`
- 密码: `admin123`
- 用户类型: 超级管理员

**注意：** 如果用户已存在，会报错，这是正常的。你也可以通过 Web 界面的注册页面创建新用户。

---

### 步骤 9: 启动应用

现在可以启动应用了。

**使用 Flask 开发服务器（推荐用于开发测试）：**

**Windows:**
```powershell
python manage.py runserver -h 0.0.0.0
```

**Linux/Mac:**
```bash
python3 manage.py runserver -h 0.0.0.0
```

或者直接使用 Flask：

```bash
flask run --host=0.0.0.0 --port=8000
```

**使用 Gunicorn（推荐用于生产环境）：**

**Windows:**
```powershell
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app('development')"
```

**Linux/Mac:**
```bash
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app('development')"
```

启动成功后，你会看到类似以下的输出：

```
 * Running on http://0.0.0.0:8000/ (Press CTRL+C to quit)
```

---

### 步骤 10: 访问应用

打开浏览器，访问：

```
http://localhost:8000
```

或者：

```
http://127.0.0.1:8000
```

如果一切正常，你应该能看到短网址服务的主页。

**登录：**
- 点击登录按钮或访问 `http://localhost:8000/auth/login`
- 使用步骤 8 创建的测试用户登录，或通过注册页面创建新账户

---

## 常见问题

### 1. 虚拟环境激活失败

**Windows PowerShell 执行策略错误：**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Linux/Mac 权限错误：**
```bash
chmod +x venv/bin/activate
```

### 2. 依赖安装失败

- 确保已激活虚拟环境
- 确保 pip 已升级到最新版本
- 如果遇到编译错误，检查是否安装了 C++ 编译工具（Windows 需要 Visual Studio Build Tools）

### 3. 数据库初始化失败

- 确保已创建 `env/env.yml` 文件
- 检查是否有文件写入权限
- 如果迁移失败，可以尝试删除 `app.sqlite` 文件后重新运行 `db upgrade`

### 4. 应用启动失败

- 检查端口 8000 是否被占用
- 检查 `env/env.yml` 配置是否正确
- 查看错误日志，根据提示解决问题

### 5. 无法访问应用

- 确保应用已成功启动
- 检查防火墙设置
- 如果使用 `0.0.0.0`，确保可以从外部访问（生产环境注意安全）

---

## 下一步

- 阅读 `README.md` 了解项目功能
- 阅读 `dev.md` 了解开发相关说明
- 查看 `app/` 目录了解代码结构
- 根据需要修改配置和代码

---

## 停止应用

在运行应用的终端中按 `Ctrl + C` 停止应用。

## 停用虚拟环境

完成后，可以停用虚拟环境：

```bash
deactivate
```

---

## 生产环境部署

对于生产环境，建议：

1. 使用 Gunicorn 或 uWSGI 作为 WSGI 服务器
2. 使用 Nginx 作为反向代理
3. 使用 MySQL 或 PostgreSQL 替代 SQLite
4. 配置 HTTPS
5. 设置环境变量而不是使用配置文件
6. 使用进程管理器（如 systemd、supervisor）管理应用

详细的生产环境部署说明请参考项目文档或联系维护者。

---

## 获取帮助

如果遇到问题：

1. 查看项目的 Issues: https://github.com/notfresh/shorturl_service/issues
2. 查看项目文档
3. 联系维护者（见 README.md）

---

**祝你使用愉快！** 🎉

