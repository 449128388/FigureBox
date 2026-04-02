# FigureBox - 手办管理系统

## 项目介绍

FigureBox是一个专为二次元手办爱好者设计的管理系统，用于管理已存在的二次元手办信息、预定商品尾款和到期日期管理、用户认证和用户管理等功能。

## 技术栈

### 后端
- Python 3.11
- FastAPI
- JWT (JSON Web Token) 认证
- SQLAlchemy ORM
- MySQL 数据库
- Pydantic 数据验证

### 前端
- Vue 3
- Vue Router 4
- Pinia (状态管理)
- Axios (API请求)
- Element Plus (UI组件库)
- Vite (构建工具)

### 部署
- Docker
- Docker Compose
- Nginx

## 功能特性

### 1. 用户认证
- 注册新用户
- 用户登录
- JWT令牌认证（60分钟过期，支持自动续期）
- Token自动续期机制（用户活跃时自动延长会话，以最后一次操作时间为准）
- 安全的认证机制，防止未授权访问

### 2. 手办管理
- 手办信息的增删改查
- 手办详情查看（独立路由页面）
- 手办图片上传（支持最多10张图片，每张不超过20MB）
- 图片预览和删除功能（鼠标悬停显示操作按钮）
- 多币种定价（支持人民币、日元、美元、欧元）
- 价格输入限制（非负整数）
- 图片删除二次确认
- **高级搜索功能**：
  - 支持名称模糊搜索
  - 入手时间时间段搜索（开始日期-结束日期）
  - 入手形式筛选（预定/现货/二手/散货/国产/其他）
  - 标签筛选（支持多标签筛选）
- 手办删除时的尾款关联校验
- 支持日文名录入（1-100字符，自动过滤emoji）
- **数量字段管理**：支持记录手办数量，控制可创建订单数量
- 智能字段显示（空值字段自动隐藏，避免"未设置"提示）
- 详情页分区展示（基本信息、规格信息、作者信息、购买信息）

### 3. 标签系统
- 手办标签管理（增删改查）
- 多标签关联手办
- 按标签筛选手办

### 4. 尾款管理（订单管理）
- **多订单支持**：单个手办支持多个订单
- 预定商品的添加、编辑和删除
- 尾款和到期日期管理
- 订单状态跟踪（未支付/已支付/已取消/已完成）
- **多层级订单管理交互方案**：
  - 支持单个手办多个订单的展示和管理
  - 添加订单切换标签，显示订单状态
  - 实现订单快速切换功能
- 状态筛选Tab（快速查看不同状态的订单）
- 购买店铺和店铺联系方式记录
- 物流订单号跟踪
- **出荷日期倒计时提醒**（不同颜色标识紧急程度）
- **订单数量限制**：单款手办可新增的订单数量严格等于手办详情页的「数量」字段值
- **唯一性过滤**：已添加过订单的手办不展示在选择列表中

### 5. 用户管理
- 个人资料查看和编辑
- 管理员权限管理
- 个人资料页面添加退出按钮

### 6. 界面功能
- 可折叠侧边栏菜单（实现模块快速切换）
- 现代化卡片式设计
- 用户信息显示和退出按钮
- 响应式布局
- 搜索栏布局优化
- 手办详情页面图片预览功能（点击大图查看原始大小）
- 图片切换功能（点击缩略图切换主图）
- 分页功能（支持自定义每页显示数量）
- 智能空值处理（空字段自动隐藏，页面更简洁）

## 项目结构

```
FigureBox/
├── backend/           # 后端代码
│   ├── app/
│   │   ├── api/       # API路由
│   │   │   ├── auth.py      # 认证相关接口
│   │   │   ├── figures.py   # 手办管理接口
│   │   │   ├── orders.py    # 订单管理接口
│   │   │   └── users.py     # 用户管理接口
│   │   ├── models/    # 数据库模型
│   │   │   ├── database.py  # 数据库连接
│   │   │   ├── figure.py    # 手办模型
│   │   │   ├── order.py     # 订单模型
│   │   │   ├── tag.py       # 标签模型
│   │   │   └── user.py      # 用户模型
│   │   ├── schemas/   # Pydantic数据验证模型
│   │   └── utils/     # 工具函数
│   │       ├── jwt.py       # JWT令牌工具
│   │       └── password.py  # 密码加密工具
│   ├── main.py        # 后端入口
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/          # 前端代码
│   ├── src/
│   │   ├── components/ # 组件
│   │   │   └── Sidebar.vue  # 侧边栏组件
│   │   ├── views/     # 页面
│   │   │   ├── Home.vue         # 首页
│   │   │   ├── Login.vue        # 登录页
│   │   │   ├── Register.vue     # 注册页
│   │   │   ├── Figures.vue      # 手办管理页
│   │   │   ├── FigureDetail.vue # 手办详情页
│   │   │   ├── Orders.vue       # 尾款管理页
│   │   │   └── Profile.vue      # 个人资料页
│   │   ├── router/    # 路由配置
│   │   ├── store/     # Pinia状态管理
│   │   └── axios/     # Axios配置和拦截器
│   ├── public/
│   ├── package.json
│   ├── vite.config.js
│   ├── nginx.conf     # Nginx配置文件
│   ├── index.html
│   └── Dockerfile
├── changes/           # 更新日志目录
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
- `GET /api/figures/` - 获取所有手办（支持搜索过滤）
- `GET /api/figures/{id}` - 获取手办详情
- `POST /api/figures/` - 创建新手办（需要认证）
- `PUT /api/figures/{id}` - 更新手办信息（需要认证）
- `DELETE /api/figures/{id}` - 删除手办（需要认证）

### 标签相关
- `GET /api/figures/tags` - 获取所有标签
- `POST /api/figures/tags` - 创建新标签（需要认证）
- `PUT /api/figures/tags/{id}` - 更新标签（需要认证）
- `DELETE /api/figures/tags/{id}` - 删除标签（需要认证）

### 订单相关
- `GET /api/orders/` - 获取用户订单或所有订单（管理员权限）
- `GET /api/orders/{id}` - 获取订单详情
- `GET /api/orders/unpaid-balance/` - 获取未支付尾款总额
- `POST /api/orders/` - 创建新订单（需要认证）
- `PUT /api/orders/{id}` - 更新订单信息（需要认证）
- `DELETE /api/orders/{id}` - 删除订单（需要认证）

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
7. 登录状态有效期为60分钟，期间有操作会自动续期

## 开发指南

### 后端开发
1. 进入 backend 目录
2. 创建虚拟环境：`python -m venv venv`
3. 激活虚拟环境：`venv\Scripts\activate` (Windows) 或 `source venv/bin/activate` (Linux/Mac)
4. 安装依赖：`pip install -r requirements.txt`
5. 运行开发服务器：`uvicorn main:app --reload --host 0.0.0.0 --port 8000`

### 前端开发
1. 进入 frontend 目录
2. 安装依赖：`npm install`
3. 运行开发服务器：`npm run dev`

## 更新日志

项目更新日志保存在 `changes/` 目录下，按日期命名：
- `2026-04-01.md` - 4月1日更新内容
- `2026-04-02.md` - 4月2日更新内容

## 许可证

GNU Affero General Public License v3.0
