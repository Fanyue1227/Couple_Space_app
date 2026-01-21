# Couple Space - 后端服务器部署指南

本指南将帮助你将后端服务部署到你的服务器上。

## 1. 环境要求

- **Python**: 3.9 或更高版本
- **Database**: MySQL 5.7 或 8.0

## 2. 部署步骤

### 第一步：上传代码

将 `backend` 文件夹上传到服务器，例如 `/www/wwwroot/qlxz_backend`。

### 第二步：配置环境

```bash
cd /www/wwwroot/qlxz_backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 复制配置文件并填写数据库信息
cp .env.example .env
nano .env  # 修改数据库连接信息
```

### 第三步：配置数据库

在 MySQL 中创建数据库：

```sql
CREATE DATABASE qlxz_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 第四步：启动服务

```bash
# 后台运行
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
```

## 3. App 端配置

App 首次打开时输入：`http://你的服务器IP:8000`

## 4. 常见问题

- **数据库连接失败**: 检查 `.env` 中的配置
- **图片上传失败**: 确保 `static/uploads` 目录有写入权限 (chmod 777)
