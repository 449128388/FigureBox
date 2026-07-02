# FigureBox - 手办管理系统

## 项目介绍

FigureBox 是一个专为二次元手办爱好者设计的一站式管理系统，同时提供 **倒狗模式**（交易者视角：资产管理、持仓分析、利润核算、HPI 指数）和 **收藏家模式**（收藏者视角：收藏柜展示、评分、厂商追踪、分享主页）两种使用模式，帮助用户全面管理手办资产。

## 技术栈

### 后端
- Python 3.11 + FastAPI
- SQLAlchemy ORM + MySQL 8.0
- JWT 认证 + 自动续期
- APScheduler 定时任务（HPI 跑批、汇率同步、持仓快照）
- Pydantic v2 数据验证

### 前端
- Vue 3 + Composition API
- Vue Router 4 + Pinia 状态管理
- Element Plus UI 组件库
- ECharts 图表（HPI 走势图、资产曲线）
- Axios HTTP 客户端
- Vite 构建工具

### 部署
- Docker + Docker Compose
- Nginx 反向代理
- 多阶段构建优化

## 功能特性

### 1. 双模式切换
- **倒狗模式**：资产仪表盘、持仓列表、HPI 塑料小人指数、交易记录、利润分析
- **收藏家模式**：收藏柜管理、手办评分、厂商追踪、隐私设置、分享主页

### 2. 资产仪表盘（倒狗模式）
- 资产总览：总市值、总成本、总盈亏、日盈亏
- 持仓列表：分产品展示持仓数量、均价、市值、盈亏
- 持仓筛选：按产品、成本价、盈亏率、库存数多维度筛选
- 指数对比：HPI 指数 vs 累计收益率走势对比
- 日变动展示：每日市值/盈亏变化
- 利润分析：已实现利润 vs 浮动盈亏
- 快速卖出：持仓手办一键快速卖出

### 3. 塑料小人指数 HPI
- **HPI = 1000 × (1 + 加权平均收益率)**，类比股票指数
- 加权平均收益率 = Σ(每手办收益率 × 该手办权重)
- 权重 = 该手办历史交易金额 / 历史总交易金额
- 在柜/已出双线走势图（绿色实线 + 灰色虚线）
- 涨红跌绿配色（中国股市习惯）
- 每日 00:30 自动跑批计算
- 成分股明细：首次买入价、累计金额、收益率、权重、贡献度

### 4. 交易记录
- 买入订单创建/编辑/删除，支持定金+尾款模式
- 卖出订单创建，支持多平台（闲鱼、淘宝等）
- 尾款支付确认与管理
- 月度交易统计与利润分析
- 账单导出
- 多币种支持（CNY/JPY/USD/EUR），自动汇率转换

### 5. 手办管理
- 手办 CRUD：名称、厂商、比例、尺寸、材质、发行年份等
- 图片上传（最多 10 张，每张 < 20MB），支持预览与删除
- 多币种定价、多标签关联
- 高级搜索：名称模糊搜索、入手时间范围、入手形式、标签筛选
- 日文名录入（自动过滤 emoji）
- 数量字段控制可创建订单数量
- CSV 导入导出

### 6. 订单管理
- 多订单支持（单个手办可有多笔订单）
- 定金预定/全款预定/现货/补仓类型
- 订单状态：未支付 → 已支付 → 已完成 / 已取消
- 出荷日期倒计时提醒（颜色标识紧急程度）
- 店铺信息、物流单号记录
- 订单数量限制（不可超过手办数量字段值）

### 7. 收藏家模式
- 收藏柜管理：创建多个收藏柜，将手办放入不同柜子
- 手办评分系统（1-5 星）
- 厂商/制造商管理
- 隐私设置：控制个人主页对外展示内容
- 分享主页：对外展示收藏概要、收藏柜、热门收藏
- 动态时间线：记录收藏活动

### 8. 汇率系统
- 自动从中国外汇交易中心获取实时汇率
- 支持 CNY/USD/JPY/EUR/HKD/GBP
- 工作日 09:25 自动同步
- 缓存有效期 3 小时，兜底默认汇率
- 所有订单金额统一转换为人民币存储

### 9. 用户与认证
- 注册/登录，JWT 令牌认证（60 分钟过期，活跃自动续期）
- 个人资料编辑
- 管理员权限管理

## 项目结构

```
FigureBox/
├── backend/                          # 后端代码
│   ├── app/
│   │   ├── api/                      # API 路由
│   │   │   ├── assets/               # 资产相关（持仓、分布、利润、指数等）
│   │   │   ├── collector/            # 收藏家相关（柜子、评分、分享、时间线等）
│   │   │   ├── market/               # 市场相关（HPI 看板、历史、成分股）
│   │   │   ├── records/              # 交易记录相关（流水、统计、导出、尾款等）
│   │   │   ├── auth.py               # 用户认证
│   │   │   ├── users.py              # 用户管理
│   │   │   ├── figures.py            # 手办 CRUD
│   │   │   ├── orders.py             # 买入订单
│   │   │   ├── sold_orders.py        # 卖出订单
│   │   │   └── asset_transactions.py # 资产交易流水
│   │   ├── models/                   # 数据库模型（16 个模块）
│   │   │   ├── user.py, figure.py, order.py, sold_order.py
│   │   │   ├── asset.py, tag.py, hpi.py, exchange_rate.py
│   │   │   ├── holding_snapshot.py, activity_feed.py
│   │   │   ├── cabinet_*.py, collector_privacy.py
│   │   │   └── ... 等
│   │   ├── schemas/                  # Pydantic 数据验证
│   │   ├── services/                 # 业务逻辑层
│   │   │   ├── dashboard_service/    # 仪表盘服务（资产/市场/交易）
│   │   │   ├── exchange_rate_service/# 汇率获取与缓存
│   │   │   ├── figure_service/       # 手办 CRUD 与价格
│   │   │   ├── order_service/        # 订单业务
│   │   │   ├── sold_order_service/   # 卖出订单业务
│   │   │   ├── collector_service/    # 收藏家业务
│   │   │   ├── scheduler_service/    # 定时任务
│   │   │   └── ... 等
│   │   └── utils/                    # 工具（JWT、密码加密等）
│   ├── migrations/                   # 数据库迁移脚本
│   ├── main.py                       # 后端入口
│   ├── entrypoint.sh                 # 容器启动脚本（自动迁移）
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env
├── frontend/                         # 前端代码
│   ├── src/
│   │   ├── components/               # 通用组件
│   │   │   └── Sidebar.vue           # 侧边栏导航
│   │   ├── views/                    # 页面
│   │   │   ├── Dashboard.vue         # 仪表盘主页面（含双模式切换）
│   │   │   ├── Dashboard/            # 仪表盘子组件
│   │   │   │   └── components/
│   │   │   │       ├── reseller/     # 倒狗模式组件
│   │   │   │       │   ├── assets/   # 资产视图组件
│   │   │   │       │   ├── market/   # 市场视图组件
│   │   │   │       │   └── trade/    # 交易视图组件
│   │   │   │       └── collector/    # 收藏家模式组件
│   │   │   ├── Figures.vue, FigureDetail.vue    # 手办管理
│   │   │   ├── Orders.vue, SoldOrders.vue       # 订单管理
│   │   │   ├── Home.vue, Login.vue, Register.vue, Profile.vue
│   │   │   └── ShareProfile.vue      # 分享主页
│   │   ├── router/                   # 路由配置
│   │   ├── store/                    # Pinia 状态管理
│   │   └── axios/                    # Axios 拦截器
│   ├── nginx.conf
│   ├── Dockerfile
│   └── package.json
├── changes/                          # 更新日志（按日期归档）
├── docker-compose.yml
├── .env
└── README.md
```

## 安装部署

### 前提条件
- Docker & Docker Compose

### 部署步骤

1. **配置环境变量**
   - 编辑 `.env` 文件，设置数据库和后端配置

2. **启动服务**
   ```bash
   # 构建并启动所有服务
   docker-compose up -d --build
   ```

3. **访问应用**
   - 前端：http://localhost:28620
   - 后端 API 文档：http://localhost:28610/docs

## 后端 API 端点

### 认证
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 注册新用户 |
| POST | `/api/auth/login` | 用户登录 |

### 用户
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/users/me` | 获取当前用户信息 |
| PUT | `/api/users/me` | 更新当前用户信息 |
| GET | `/api/users/` | 获取所有用户（管理员） |

### 手办
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/figures/` | 获取手办列表（支持搜索过滤） |
| GET | `/api/figures/{id}` | 获取手办详情 |
| POST | `/api/figures/` | 创建新手办 |
| PUT | `/api/figures/{id}` | 更新手办 |
| DELETE | `/api/figures/{id}` | 删除手办 |
| GET | `/api/figures/export` | 导出手办 CSV |
| POST | `/api/figures/import` | 导入手办 CSV |

### 标签
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/figures/tags` | 获取所有标签 |
| POST | `/api/figures/tags` | 创建标签 |
| PUT | `/api/figures/tags/{id}` | 更新标签 |
| DELETE | `/api/figures/tags/{id}` | 删除标签 |

### 订单
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/orders/` | 获取订单列表 |
| GET | `/api/orders/{id}` | 获取订单详情 |
| GET | `/api/orders/unpaid-balance/` | 获取未付尾款总额 |
| POST | `/api/orders/` | 创建订单 |
| PUT | `/api/orders/{id}` | 更新订单 |
| DELETE | `/api/orders/{id}` | 删除订单 |

### 市场
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/market/dashboard` | HPI 看板数据 |
| GET | `/api/market/hpi-history` | HPI 历史走势 |
| GET | `/api/market/hpi-components` | HPI 成分股明细 |

### 资产
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/assets/dashboard` | 资产看板数据 |
| GET | `/api/assets/positions` | 持仓列表 |
| GET | `/api/assets/distribution` | 资产分布 |
| GET | `/api/assets/profit-analysis` | 利润分析 |
| GET | `/api/assets/holding-filter` | 持仓筛选 |
| GET | `/api/exchange-rates` | 汇率查询 |

### 收藏家
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/collector/dashboard` | 收藏家仪表盘 |
| GET | `/api/collector/cabinets` | 收藏柜管理 |
| GET | `/api/collector/manufacturers` | 厂商管理 |
| GET | `/api/collector/ratings` | 手办评分 |
| GET | `/api/collector/share` | 分享主页 |

## 前端页面

| 路径 | 页面 | 说明 |
|------|------|------|
| `/home` | 首页 | 模式选择入口 |
| `/login` | 登录 | 用户登录 |
| `/register` | 注册 | 新用户注册 |
| `/dashboard` | 仪表盘 | 双模式主面板（倒狗/收藏家） |
| `/figures` | 手办列表 | 管理所有手办 |
| `/figures/:id` | 手办详情 | 单款手办完整信息 |
| `/orders` | 买入订单 | 管理定金预定/尾款 |
| `/sold-orders` | 卖出订单 | 管理已出售手办 |
| `/profile` | 个人中心 | 资料编辑 |
| `/share/:userId` | 分享主页 | 对外展示的收藏主页 |

## 环境变量

```env
# 数据库
MYSQL_ROOT_PASSWORD=root
MYSQL_USER=admin
MYSQL_PASSWORD=password
MYSQL_DATABASE=figurebox

# 后端
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=mysql+pymysql://admin:password@db:3306/figurebox
```

## 定时任务

| 任务 | 时间 | 说明 |
|------|------|------|
| HPI 每日跑批 | 每日 00:30 | 计算所有用户当日 HPI |
| 持仓快照 | 每日 23:30 | 记录持仓快照用于历史走势 |
| 汇率同步 | 工作日 09:25 | 从中国外汇交易中心同步汇率 |
| 汇率锁清理 | 每日 00:10 | 清除汇率并发锁，确保任务正常执行 |

## 更新日志

项目更新日志保存在 `changes/` 目录下，按月归档：
- `changes/2026-03/` — 3 月更新
- `changes/2026-04/` — 4 月更新
- `changes/2026-05/` — 5 月更新
- `changes/2026-06/` — 6 月更新
- `changes/2026-07/` — 7 月更新

## 注意事项

1. 首次部署时，容器启动脚本会自动创建所需的表结构
2. 生产环境请修改 `SECRET_KEY` 为安全的随机字符串
3. 图片上传限制：最多 10 张，每张不超过 20MB，Nginx 已配置 250MB 上限
4. 登录状态有效期为 60 分钟，有操作会自动续期
5. 汇率数据来源于中国外汇交易中心（工作日 09:25 发布），非工作日使用最近交易日数据
6. HPI 指数使用人民币计价，外币订单通过汇率转换后参与计算

## 开发指南

### 后端开发
```bash
cd backend
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 前端开发
```bash
cd frontend
npm install
npm run dev
```

## 许可证

GNU Affero General Public License v3.0
