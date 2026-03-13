# FigureBox - 手办管理系统

## 项目介绍

FigureBox是一个专为二次元手办爱好者设计的管理系统，用于管理已存在的二次元手办信息、预定商品尾款和到期日期管理、用户认证和用户管理等功能。

## 技术栈

### 后端
- Python 3.9
- FastAPI
- JWT (JSON Web Token) 认证
- SQLAlchemy ORM
- MySQL 数据库

### 前端
- Vue 3
- Vue Router
- Pinia (状态管理)
- Axios (API请求)
- Vite (构建工具)

### 部署
- Docker
- Docker Compose

## 功能特性

1. **用户认证**
   - 注册新用户
   - 用户登录
   - JWT令牌认证（30分钟过期）

2. **手办管理**
   - 手办信息的增删改查
   - 手办详情查看（独立路由页面）
   - 手办图片上传（支持最多10张图片，每张不超过20MB）
   - 图片预览和删除功能（鼠标悬停显示操作按钮）
   - 多币种定价（支持人民币、日元、美元、欧元）
   - 价格输入限制（非负整数）
   - 图片删除二次确认
   - 搜索功能（支持名称、入手时间、入手形式搜索）
   - 入手时间时间段搜索
   - 手办删除时的尾款关联校验

3. **尾款管理**
   - 预定商品的添加
   - 尾款和到期日期管理
   - 订单状态跟踪
   - 完整的添加、编辑和删除功能

4. **用户管理**
   - 个人资料查看和编辑
   - 管理员权限管理
   - 个人资料页面添加退出按钮

5. **界面功能**
   - 可折叠侧边栏菜单（实现模块快速切换）
   - 现代化卡片式设计
   - 用户信息显示和退出按钮
   - 响应式布局
   - 搜索栏布局优化
   - 手办详情页面图片预览功能（点击大图查看原始大小）
   - 图片切换功能（点击缩略图切换主图）

## 项目结构

```
FigureBox/
├── backend/           # 后端代码
│   ├── app/
│   │   ├── api/       # API路由
│   │   ├── models/    # 数据库模型
│   │   ├── schemas/   # 数据验证
│   │   └── utils/     # 工具函数
│   ├── main.py        # 后端入口
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/          # 前端代码
│   ├── src/
│   │   ├── components/ # 组件
│   │   ├── views/     # 页面
│   │   ├── router/    # 路由
│   │   ├── store/     # 状态管理
│   │   └── axios/     # API请求
│   ├── public/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── Dockerfile
├── docker-compose.yml # Docker Compose配置
└── .env               # 环境变量
```

## 安装部署

### 前提条件
- Docker
- Docker Compose

### 部署步骤

1. **克隆项目**

2. **配置环境变量**
   - 编辑 `.env` 文件，设置数据库和后端配置

3. **启动服务**
   ```bash
   # 构建并启动所有服务
   docker-compose up -d --build
   
   # 仅构建并启动后端服务
   docker-compose up -d --build backend
   
   # 仅构建并启动前端服务
   docker-compose up -d --build frontend
   ```

4. **访问应用**
   - 前端：http://localhost:25600
   - 后端API文档：http://localhost:25610/docs

## 后端API端点

### 认证相关
- `POST /api/auth/register` - 注册新用户
- `POST /api/auth/login` - 用户登录

### 用户相关
- `GET /api/users/me` - 获取当前用户信息
- `PUT /api/users/me` - 更新当前用户信息
- `GET /api/users/` - 获取所有用户（管理员权限）

### 手办相关
- `GET /api/figures/` - 获取所有手办
- `GET /api/figures/{id}` - 获取手办详情
- `POST /api/figures/` - 创建新手办（管理员权限）
- `PUT /api/figures/{id}` - 更新手办信息（管理员权限）
- `DELETE /api/figures/{id}` - 删除手办（普通用户也可操作）

### 订单相关
- `GET /api/orders/` - 获取用户订单或所有订单（管理员权限）
- `GET /api/orders/{id}` - 获取订单详情
- `POST /api/orders/` - 创建新订单
- `PUT /api/orders/{id}` - 更新订单信息
- `DELETE /api/orders/{id}` - 删除订单

## 前端页面

- `/home` - 首页
- `/login` - 登录页面
- `/register` - 注册页面
- `/figures` - 手办管理页面
- `/figures/:id` - 手办详情页面
- `/orders` - 尾款管理页面
- `/profile` - 个人资料页面

## 环境变量配置

### .env 文件
```env
# 数据库配置
MYSQL_ROOT_PASSWORD=root
MYSQL_USER=admin
MYSQL_PASSWORD=password
MYSQL_DATABASE=figurebox

# 后端配置
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=mysql+pymysql://admin:password@db:3306/figurebox
```

## 注意事项

1. 首次部署时，数据库会自动创建所需的表结构
2. 生产环境中请修改 `SECRET_KEY` 为安全的随机字符串
3. 生产环境中请修改数据库密码为强密码
4. 前端开发环境下，Vite 代理已配置为指向后端API地址
5. 图片上传限制：最多支持10张图片，每张不超过20MB
6. Nginx已配置支持大文件上传（250MB）

## 开发指南

### 后端开发
1. 进入 backend 目录
2. 安装依赖：`pip install -r requirements.txt`
3. 运行开发服务器：`uvicorn main:app --reload`

### 前端开发
1. 进入 frontend 目录
2. 安装依赖：`npm install`
3. 运行开发服务器：`npm run dev`

## 许可证

GNU Affero General Public License v3.0
