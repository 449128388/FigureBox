# FigureBox 安装指南

> 适用：FigureBox 项目的完整安装与部署说明。
> Windows 用户的详细安装步骤请直接跳到 [🪟 Windows 小白友好安装指南](#-windows-小白友好安装指南小白友好版) 章节。

---

## 目录

- [服务端口说明](#服务端口说明)
- [🪟 Windows 小白友好安装指南（小白友好版）](#-windows-小白友好安装指南小白友好版)
- [🍎 macOS 安装步骤](#-macos-安装步骤)
- [🐧 Linux (Ubuntu) 安装步骤](#-linux-ubuntu-安装步骤)
- [本地开发模式（不使用 Docker）](#本地开发模式不使用-docker)

---

## 服务端口说明

| 服务 | 端口 | 说明 |
|------|------|------|
| 前端 | 28620 | Web 访问入口 |
| 后端 | 28610 | REST API 服务 |
| MySQL | 28630 | 数据库 |
| MinIO API | 28640 | 对象存储 API |
| MinIO Console | 28641 | 对象存储管理控制台 |

---

## 🪟 Windows 小白友好安装指南（小白友好版）

> 适用：完全没接触过 Docker 的 Windows 用户。一步一步跟着做即可。

### 第 1 步：检查 Windows 版本

按 `Win + R` → 输入 `winver` → 回车，查看 Windows 版本。

- ✅ **Windows 10 64位（版本 2004 或更高，推荐 22H2）** - 满足要求
- ✅ **Windows 11 64位** - 满足要求
- ❌ Windows 7 / 8 / 10 32位 - 不支持

> 💡 **小提示**：版本号可以在「设置 → 系统 → 关于」中查看，比如"Windows 10 家庭中文版 22H2"。

### 第 2 步：开启 CPU 虚拟化（VT-x / AMD-V）

大部分电脑默认已开启，如果后面启动 Docker 报错 `Hardware assisted virtualization and data execution protection must be enabled in the BIOS`，需要进入 BIOS 开启。

- 重启电脑 → 开机时连续按 `Del` / `F2` / `F10`（根据主板不同）进入 BIOS
- 找到 `Advanced` → `CPU Configuration`
- 把 `Intel Virtualization Technology`（Intel 处理器）或 `SVM Mode`（AMD 处理器）设为 `Enabled`
- 保存退出（通常是 `F10` → `Yes`）

### 第 3 步：启用 WSL 2（推荐方式）

> WSL 2 是 Windows 官方的 Linux 子系统，Docker Desktop 会基于它运行，性能比旧的 Hyper-V 更好。

#### 3.1 启用 WSL 功能

以**管理员身份**打开 PowerShell（右键开始菜单 → `Windows PowerShell (管理员)`），执行：

```powershell
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

执行完成后**重启电脑**。

#### 3.2 设置 WSL 默认版本为 2

重启后再次以**管理员身份**打开 PowerShell，执行：

```powershell
wsl --set-default-version 2
```

### 第 4 步：下载并安装 Docker Desktop for Windows

1. 打开浏览器，访问 Docker 官网下载页：<https://www.docker.com/products/docker-desktop/>
2. 点击 `Download for Windows`（会自动下载适配你系统的版本）
3. 下载完成后双击 `Docker Desktop Installer.exe` 安装
4. 安装过程中**保持默认勾选**（"Use WSL 2 instead of Hyper-V"必须勾选）
5. 安装完成后**重启电脑**（安装程序会提示）

### 第 5 步：启动 Docker Desktop

1. 在开始菜单找到 `Docker Desktop` 并打开
2. 第一次启动会弹出服务协议，点击 `Accept`
3. 等待右下角托盘区 Docker 图标**从灰变绿**（说明 Docker 已就绪）
4. 可能需要登录 Docker Hub 账号（**可以点击跳过**，不登录也能用本地功能）

### 第 6 步：验证 Docker 是否装好

以**普通身份**打开 PowerShell 或 CMD，执行：

```powershell
docker --version
docker compose version
```

看到类似下面的输出就说明成功了：

```
Docker version 24.0.7, build afdd53b
Docker Compose version v2.23.3-desktop.2
```

### 第 7 步：下载 FigureBox 项目代码

#### 方式 A：用 Git（推荐）

如果没有 Git，先到 <https://git-scm.com/download/win> 下载安装。

打开 PowerShell，进入你想放项目的目录（比如 `D:\projects`）：

```powershell
cd D:\projects
git clone <项目仓库地址> FigureBox
cd FigureBox
```

#### 方式 B：直接下载 ZIP

1. 在 GitHub/Gitee 项目页面点击绿色 `Code` 按钮 → `Download ZIP`
2. 解压到任意目录，比如 `D:\projects\FigureBox`

### 第 8 步：检查 .env 配置文件

进入项目目录，确认根目录有 `.env` 文件（没有的话从 `.env.example` 复制一份）。

用记事本打开 `.env`，**普通用户直接用默认配置即可**，重点关注以下几个端口：

```
MYSQL_ROOT_PASSWORD=root       # 数据库 root 密码
MINIO_ROOT_USER=figurebox      # MinIO 用户名
MINIO_ROOT_PASSWORD=FigureBox@2024!  # MinIO 密码
```

> ⚠️ **重要**：如果你电脑上 28630 / 28640 / 28620 等端口已被其他程序占用（比如本地已装 MySQL），需要把 `.env` 和 `docker-compose.yml` 中的端口全部改掉（如 `28630` → `28631`）。

### 第 9 步：一键启动！

在项目根目录（包含 `docker-compose.yml` 的目录）打开 PowerShell，执行：

```powershell
docker compose up -d --build
```

> 💡 **小提示**：
> - 旧版 Docker 用 `docker-compose up -d --build`（带横线），新版本用 `docker compose up -d --build`（带空格）
> - `-d` 表示后台运行
> - `--build` 表示重新构建镜像
> - 第一次启动会下载镜像、构建前端/后端、初始化数据库，**需要 5-15 分钟**，取决于网速
> - 看到最后几行出现 `✔ Container figurebox-frontend-1 Started` 之类的输出就成功了

### 第 10 步：检查容器是否都跑起来了

执行：

```powershell
docker compose ps
```

应该看到 4 个容器都是 `running` 或 `healthy` 状态：

```
NAME                    STATUS          PORTS
figurebox-db-1          Up (healthy)    0.0.0.0:28630->3306/tcp
figurebox-backend-1     Up              0.0.0.0:28610->8000/tcp
figurebox-frontend-1    Up              0.0.0.0:28620->80/tcp
figurebox-minio-1       Up (healthy)    0.0.0.0:28640-28641->9000-9001/tcp
```

> ⚠️ 如果某个容器一直 `Restarting`，执行 `docker compose logs <容器名>` 查看错误信息。

### 第 11 步：访问应用！

打开浏览器，访问：

- 🌐 **前端主页**：<http://localhost:28620>
- 📚 **后端 API 文档**：<http://localhost:28610/docs>
- 🗄️ **MinIO 管理控制台**：<http://localhost:28641>（用户名 `figurebox`，密码 `FigureBox@2024!`）

第一次访问会自动跳到注册页面，注册账号即可使用！

### 第 12 步：常用维护命令

| 操作 | 命令 |
|------|------|
| 查看运行状态 | `docker compose ps` |
| 查看所有日志（实时） | `docker compose logs -f` |
| 查看某个服务日志 | `docker compose logs -f backend` |
| 停止服务 | `docker compose stop` |
| 启动服务 | `docker compose start` |
| 重启服务 | `docker compose restart` |
| **完全清理**（删数据！慎用） | `docker compose down -v` |
| 重新构建并启动（代码更新后） | `docker compose up -d --build` |

> 💡 修改代码后**只需要重新执行 `docker compose up -d --build`**，Docker 会自动检测变更的镜像并重建。

### ⚠️ 常见问题排查

#### Q1：启动时报 "port is already allocated"
端口被占用。修改 `docker-compose.yml` 和 `.env` 中的端口（28610/28620/28630/28640/28641）。

#### Q2：浏览器访问 28620 显示空白
先等 30 秒（前端 nginx 启动比后端慢），再 `Ctrl + F5` 强制刷新。

#### Q3：注册/登录提示 500 错误
执行 `docker compose logs backend` 看后端日志。常见原因：
- 数据库迁移未完成：执行 `docker compose restart backend` 等待 1 分钟
- 数据库密码不一致：确认 `.env` 中 `MYSQL_PASSWORD` 和 `DATABASE_URL` 一致

#### Q4：Docker Desktop 一直转圈
- 检查第 2 步的虚拟化是否开启
- 在 Docker Desktop → Settings → Resources 调小内存（4GB 即可）
- 重启 Docker Desktop（右下角托盘右键 → Restart）

#### Q5：WSL 安装报错 0x80370102
CPU 虚拟化未开启，回到第 2 步。

#### Q6：想换台电脑重新部署
1. 拉取最新代码
2. 删除旧容器和卷：`docker compose down -v`
3. 重新启动：`docker compose up -d --build`

---

## 🍎 macOS 安装步骤

```bash
# 1. 安装 Docker Desktop for Mac
# 下载地址：https://www.docker.com/products/docker-desktop/
# 拖入 Applications 文件夹即可

# 2. 启动 Docker Desktop，等待图标变绿

# 3. 克隆项目并启动
git clone <项目仓库地址> FigureBox
cd FigureBox
docker compose up -d --build

# 4. 访问 http://localhost:28620
```

## 🐧 Linux (Ubuntu) 安装步骤

```bash
# 1. 安装 Docker 和 Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# 重新登录后生效
sudo apt install -y docker-compose-plugin

# 2. 克隆项目并启动
git clone <项目仓库地址> FigureBox
cd FigureBox
docker compose up -d --build

# 3. 访问 http://localhost:28620
```

---

## 本地开发模式（不使用 Docker）

如果你是开发者想调试代码，可以本地启动前后端：

### 后端开发

```bash
cd backend

# 创建虚拟环境
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动（需先准备好 MySQL 和 MinIO，可改用 Docker 只跑这两个）
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 前端开发

```bash
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173
```
