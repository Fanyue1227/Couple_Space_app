# 情侣空间 (Couple Space) - 后端服务器部署指南

  这是一个记录情侣生活的app，有纪念日、恋爱相册、todolist功能，需要自己在服务器中部署，app首次打开时可以配置服务器信息。软件会自动缓存服务器数据，离线时也可以使用。
  在服务器部署后端之后直接手机安装软件即可，部署教程如下：

## 1. 环境要求

*   **Operating System**: Linux (推荐 Ubuntu/CentOS) 或 Windows
*   **Python**: 3.9 或更高版本
*   **Database**: MySQL 5.7 或 8.0
*   **Web Server**: Nginx (可选，推荐用于生产环境优化)

## 2. 基础部署步骤 (不使用 Nginx)

完成以下步骤后，服务器即可正常运行和访问。

### 第一步：准备代码

将 `qlxz_backend` 文件夹上传到你的服务器目录，例如 `/www/wwwroot/qlxz_backend`。

### 第二步：配置环境与依赖

进入后端目录并安装所需的 Python 依赖库。

```bash
#进入目录
cd /www/wwwroot/qlxz_backend

# 建议先创建虚拟环境 (可选)
python3 -m venv venv

  
#激活虚拟环境
source venv/bin/activate  # Linux
# .\venv\Scripts\activate # Windows

# 安装依赖
pip install -r requirements.txt
```

### 第三步：配置数据库

1.  在你的 MySQL 数据库中创建一个新的数据库，例如 `qlxz_app`。

2.  打开 `qlxz_backend` 目录下的 `.env` 文件，修改数据库连接信息：

    ```ini
    
    # file: .env
    DATABASE_URL=mysql+pymysql://你的用户名:你的密码@localhost:3306/qlxz_app?charset=utf8mb4

    ```

### 第四步：启动服务


选择以下任一方法启动服务。

#### 方法一：使用宝塔面板 Supervisor 管理器 (推荐)

1.  在宝塔面板安装 `Supervisor管理器`。

2.  添加守护进程：

    *   **名称**: `qlxz_backend`

    *   **启动用户**: `root` 或 `www`

    *   **运行目录**: `/www/wwwroot/qlxz_backend`

    *   **启动命令**: (注意端口为 8000)

        ```bash
        
        /www/wwwroot/qlxz_backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
        ```

    *   **进程数量**: 1

#### 方法二：命令行后台运行

```bash

# 1. 先进入代码目录
cd /www/wwwroot/qlxz_backend

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 后台运行 (端口 8000)
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &

# 4. 查看日志
tail -f server.log

```

**🎉 基础部署完成！**

现在你可以在 App 中输入服务器地址：`http://你的服务器IP:8000` 即可使用。
  
---

## 3. 进阶优化：配置 Nginx (推荐)

如果你希望访问速度更快、更安全，建议配合 Nginx 使用。

**注意：由于 Nginx 需要占用 8000 端口，我们需要先修改后端的端口为 8001。**

### 第一步：修改后端端口 (8000 -> 8001)

1.  **停止** 当前正在运行的后端服务 (Supervisor 或命令行进程)。

2.  **修改** 启动命令，将 `--port 8000` 改为 `--port 8001`。

    *   例如 Supervisor 命令改为：

        ```bash

        /www/wwwroot/qlxz_backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8001

        ```

3.  **重启** 后端服务，确保它在 8001 端口运行。

### 第二步：配置 Nginx


1.  使用文本编辑器修改目录下的 `nginx_qlxz.conf` 文件：

    *   将 `server_name` 改为你的公网 IP。

    *   确认 `alias` 路径正确。

    *   (文件已默认配置为监听 8000，转发给 8001)。

2.  执行以下部署命令：


```bash

# 1. (宝塔面板) 复制配置文件
cp nginx_qlxz.conf /www/server/nginx/conf/vhost/qlxz.conf

# 2. 检查配置是否有语法错误 
nginx -t

# 3. 重载 Nginx
nginx -s reload

# 4. 设置权限以防止 403 错误 (重要)
chown -R www:www /www/wwwroot/qlxz_backend/static
chmod -R 777 /www/wwwroot/qlxz_backend/static

```

  

**🎉 进阶配置完成！**

现在你依然在 App 中输入：`http://你的服务器IP:8000` (实际是通过 Nginx 访问)。

## 4. 常见问题

*   **数据库连接失败**: 检查 `.env` 用户名密码。

*   **图片上传失败**: 检查 `static/uploads` 目录权限 (chmod 777)。

*   **8000 端口无法访问**: 检查阿里云/腾讯云安全组和宝塔防火墙是否放行了 8000 端口。
