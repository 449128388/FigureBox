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
- **持仓分页**：支持每页 9/18/36 条切换、页码跳转，显示「共 X 条」
- 指数对比：HPI 指数 vs 累计收益率走势对比
- 日变动展示：每日市值/盈亏变化
- 利润分析：已实现利润 vs 浮动盈亏
- 快速卖出：持仓手办一键快速卖出
- **板块涨幅排行**：按"涨的优先于跌的"排序（涨幅降序 → 跌幅升序）
- **厂商分布饼图**：自动拆分多厂商手办（如 "Rocket Boy、PLEIADES"）

### 3. 塑料小人指数 HPI
- **HPI = 1000 × (1 + 加权平均收益率)**，类比股票指数
- 加权平均收益率 = Σ(每手办收益率 × 该手办权重)
- 权重 = 该手办历史交易金额 / 历史总交易金额
- 在柜/已出双线走势图（绿色实线 + 灰色虚线）
- 涨红跌绿配色（中国股市习惯）
- 每日 00:30 自动跑批计算
- 成分股明细：首次买入价、累计金额、收益率、权重、贡献度

### 4. 交易记录
- **买入订单三步向导**：核心信息（手办/定金/尾款/出荷/订单类型）→ 店铺与支付（店铺/支付方式/支付时间）→ 物流与备注
- **订单双支付字段**：定金支付方式/支付时间 + 尾款支付方式/支付时间，分别记录
- **多种订单状态识别**：现货、定金预定、全款预定；未支付/已支付/已完成/已取消
- **智能支付明细**：根据订单类型和状态自动选择正确的定金/尾款/全款支付字段展示
- 卖出订单创建/编辑，支持多平台（闲鱼、淘宝等）
- **卖出订单字段**：支付方式（支付宝/微信/银行卡）、卖出时间（精确到秒）
- 尾款支付确认与管理
- 月度交易统计与利润分析（含变更调整、补款、退款计算）
- 账单导出
- 多币种支持（CNY/JPY/USD/EUR），自动汇率转换
- 物流公司：顺丰/京东/德邦/EMS 等

### 5. 手办管理
- 手办 CRUD：名称、厂商、比例、尺寸、材质、发行年份等
- **图片拖拽排序**：支持通过 HTML5 拖拽自由调整图片顺序
- **外部图片自动转存**：从 HPOI 等图床抓取的图片自动上传至 MinIO
- 图片上传（最多 10 张，每张 < 20MB），支持预览与删除
- 多币种定价、多标签关联
- 高级搜索：名称模糊搜索、入手时间范围、入手形式、标签筛选
- **完整分页支持**：手办库列表带真实总数翻页（修复"共 15 条"始终等于当前页问题）
- 日文名录入（自动过滤 emoji）
- 数量字段控制可创建订单数量
- CSV 导入导出
- **手办详情页视觉重构**：1400px 容器 + 双栏 sticky 图 + 右侧 info-card 堆叠；订单多笔时 tab 切换器
- **手办详情页备注展示**：基本信息卡片中显示「备注」字段，支持换行

### 6. 订单管理
- 多订单支持（单个手办可有多笔订单）
- 定金预定/全款预定/现货/补仓类型
- 订单状态：未支付 → 已支付 → 已完成 / 已取消
- 出荷日期倒计时提醒（颜色标识紧急程度）
- 店铺信息、物流单号记录
- 订单数量限制（不可超过手办数量字段值）
- **尾款管理分页**：10/20/30/40/50 条/页
- **订单备注支持多行**：textarea 录入 + 卡片展示保留换行

### 7. 收藏家模式
- 收藏柜管理：创建多个收藏柜，将手办放入不同柜子
- 收藏柜统计：已入手/预定中/待出荷（在柜/未付尾款/已付尾款待出荷）
- 手办评分系统（1-5 星）
- **本命厂商列表**：搜索 + 状态筛选（全部/有在柜/无在柜），按总藏品数+在柜数排序
- **本命厂商详情**：多状态切换（全部/在柜/预定中/已出/愿望中）
- **本命厂商 Logo 自动转存 MinIO**
- 隐私设置：控制个人主页对外展示内容
- **分享主页**：对外展示收藏概要、收藏柜、热门收藏、真实头像/昵称
- 动态时间线：记录收藏活动

### 8. 愿望清单
- **HPOI URL 自动抓取**：智能解析定价（人民币/日元）、发售日期（多种格式）、制作商（多厂商）、涂装师（多涂装师）
- **外部图片自动转存 MinIO**
- 手动添加/编辑愿望清单项
- 发售日期组件：Element Plus DatePicker
- 备注支持换行渲染
- 状态管理：愿望中 / 已发售 / 已入手 / 已取消

### 9. 汇率系统
- 自动从中国外汇交易中心获取实时汇率
- 支持 CNY/USD/JPY/EUR/HKD/GBP
- 工作日 09:25 自动同步
- 缓存有效期 3 小时，兜底默认汇率
- 所有订单金额统一转换为人民币存储
- 汇率锁清理：每日 00:10 清除并发锁

### 10. 首页（Home）
- 投资天数统计（自首次下单起）
- 本月补款统计（待付尾款总额）
- 持仓 TOP5（仅已入库）
- 愿望清单数量统计
- 月度趋势对比
- 最近动态时间线（含新预定/补款/入库/取消等差异化文案）

### 11. 用户与认证
- 注册/登录，JWT 令牌认证（60 分钟过期，活跃自动续期）
- 个人资料编辑（昵称/头像）
- 管理员权限管理
- **登录/注册页无滚动条**：高度严格等于视口

### 12. 系统级优化
- 全局时区：东八区（Asia/Shanghai）
- 数据迁移：容器启动时自动执行数据库迁移脚本
- 字符校验：支持日文重复符号 々、中文直角引号「」、下划线 _、中间点 ·、全角感叹号 ！等
- 关于弹窗：使用真实 logo 图片
- 组件架构：Vue3 组合式 API（composables）+ 单一职责组件拆分

## 项目结构

```
FigureBox/
├── backend/                              # 后端代码
│   ├── app/
│   │   ├── api/                          # API 路由（按业务域拆分）
│   │   │   ├── assets/                   # 资产（持仓、分布、价格、筛选、汇率）
│   │   │   ├── collector/                # 收藏家（柜子、评分、厂商、分享、时间线、隐私）
│   │   │   ├── market/                   # 市场（HPI 看板、历史、成分股、K线）
│   │   │   ├── records/                  # 交易记录（流水、统计、导出、尾款、买卖单）
│   │   │   ├── auth.py                   # 用户认证
│   │   │   ├── users/                    # 用户管理（含 MinIO 配置）
│   │   │   ├── figures.py                # 手办 CRUD
│   │   │   ├── orders.py                 # 买入订单
│   │   │   ├── sold_orders.py            # 卖出订单
│   │   │   ├── wishlist.py               # 愿望清单
│   │   │   ├── home.py                   # 首页统计
│   │   │   └── share.py                  # 分享主页
│   │   ├── models/                       # 数据库模型（按域拆分）
│   │   │   ├── user.py, figure.py, order.py, sold_order.py
│   │   │   ├── asset.py, tag.py, hpi.py, exchange_rate.py
│   │   │   ├── holding_snapshot.py, activity_feed.py
│   │   │   ├── cabinet_*.py, collector_privacy.py
│   │   │   └── ... 等
│   │   ├── schemas/                      # Pydantic 数据验证
│   │   ├── services/                     # 业务逻辑层（企业级服务架构）
│   │   │   ├── dashboard_service/        # 仪表盘服务（资产/市场/交易）
│   │   │   │   ├── assets_service/       # 资产服务（持仓/分布/利润/筛选）
│   │   │   │   ├── market_service/       # 市场服务（HPI/板块/K线）
│   │   │   │   └── trade_records_service/# 交易流水服务（买入/卖出）
│   │   │   ├── exchange_rate_service/    # 汇率获取与缓存
│   │   │   ├── figure_service/           # 手办 CRUD 与价格
│   │   │   ├── order_service/            # 订单业务（含 CRUD/Query/Transaction）
│   │   │   ├── sold_order_service/       # 卖出订单业务
│   │   │   ├── collector_service/        # 收藏家业务（柜子/评分/厂商/活动）
│   │   │   ├── wishlist_service/         # 愿望清单业务
│   │   │   ├── share_service/            # 分享主页业务
│   │   │   ├── home_service/             # 首页统计业务
│   │   │   ├── storage_service/          # MinIO 对象存储（含外部图片转存）
│   │   │   ├── scheduler_service/        # 定时任务（HPI/汇率/快照）
│   │   │   └── user_profile_service/     # 用户资料与 MinIO 配置
│   │   ├── migrations/                   # 数据库迁移脚本（启动时自动执行）
│   │   ├── scripts/                      # 维护脚本（如列注释修复）
│   │   └── utils/                        # 工具（JWT、密码、中间件、时区）
│   ├── main.py                           # 后端入口（含中间件注册）
│   ├── entrypoint.sh                     # 容器启动脚本（自动迁移）
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env
├── frontend/                             # 前端代码
│   ├── src/
│   │   ├── components/                   # 通用组件
│   │   │   ├── TopHeader.vue             # 顶部导航
│   │   │   └── Sidebar.vue               # 侧边栏
│   │   ├── views/                        # 页面
│   │   │   ├── Dashboard.vue             # 仪表盘主页面（含双模式切换）
│   │   │   ├── Dashboard/                # 仪表盘子组件（按模式 + composables 拆分）
│   │   │   │   ├── composables/          # 业务逻辑组合式函数
│   │   │   │   └── components/
│   │   │   │       ├── reseller/         # 倒狗模式组件
│   │   │   │       │   ├── assets/       # 资产视图组件
│   │   │   │       │   ├── market/       # 市场视图组件
│   │   │   │       │   └── trade/        # 交易视图组件
│   │   │   │       └── collector/        # 收藏家模式组件
│   │   │   │           ├── ActivityFeed/         # 活动时间线（含 api/composables）
│   │   │   │           ├── CabinetDetail/        # 收藏柜详情（多子组件）
│   │   │   │           ├── ManufacturerList/     # 本命厂商（含 composables）
│   │   │   │           ├── PrivacySettings/      # 隐私设置（含 composables）
│   │   │   │           └── SharePoster/          # 分享海报
│   │   │   ├── Figures.vue               # 手办库列表
│   │   │   ├── FigureDetail/             # 手办详情（按职责拆分多个子组件）
│   │   │   ├── Orders/                   # 订单管理（三步向导 + composables）
│   │   │   ├── SoldOrders/               # 卖出订单
│   │   │   ├── Wishlist/                 # 愿望清单
│   │   │   ├── Home.vue, Login.vue, Register.vue, Profile.vue
│   │   │   └── ShareProfile.vue          # 分享主页
│   │   ├── router/                       # 路由配置
│   │   ├── store/                        # Pinia 状态管理
│   │   └── axios/                        # Axios 拦截器（含 token 续期）
│   ├── nginx.conf
│   ├── Dockerfile
│   └── package.json
├── changes/                              # 更新日志（按月归档）
├── docker/                               # Docker 辅助配置
│   └── mysql/                            # MySQL 配置 + 初始化 SQL
├── docker-compose.yml
├── .env
└── README.md
```

## 安装部署

> 详细的安装步骤（特别是 Windows 用户的 12 步小白友好指南）已抽离到独立文档 **[INSTALL.md](INSTALL.md)**，请前往查看。

### 适用平台
- ✅ Windows 10 / Windows 11
- ✅ macOS 12+
- ✅ Linux（Ubuntu 20.04+ / CentOS 8+）

### 服务端口说明
| 服务 | 端口 | 说明 |
|------|------|------|
| 前端 | 28620 | Web 访问入口 |
| 后端 | 28610 | REST API 服务 |
| MySQL | 28630 | 数据库 |
| MinIO API | 28640 | 对象存储 API |
| MinIO Console | 28641 | 对象存储管理控制台 |

### 快速开始（3 步）

如果你已有 Docker 环境，可直接：

```bash
# 1. 进入项目目录
cd FigureBox

# 2. 一键启动所有服务
docker compose up -d --build

# 3. 浏览器访问
# 前端：http://localhost:28620
# 后端 API：http://localhost:28610/docs
```

> 💡 第一次启动会下载镜像、构建前后端、初始化数据库，**约需 5-15 分钟**。

### 详细安装文档

- 🪟 **Windows 小白友好指南（12 步 + 6 个常见问题）** → 查看 [INSTALL.md](INSTALL.md)
- 🍎 macOS / 🐧 Linux 安装 → 查看 [INSTALL.md](INSTALL.md)
- 🛠 本地开发模式（不使用 Docker）→ 查看 [INSTALL.md](INSTALL.md)

## 后端 API 端点

> 完整 API 文档可在部署后访问 <http://localhost:28610/docs> 查看。

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
| GET/PUT/POST | `/api/users/minio-config` | MinIO 配置接口（所有已登录用户可用） |

### 手办
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/figures/` | 获取手办列表（支持搜索过滤 + 分页） |
| GET | `/api/figures/{id}` | 获取手办详情 |
| POST | `/api/figures/` | 创建新手办 |
| PUT | `/api/figures/{id}` | 更新手办 |
| DELETE | `/api/figures/{id}` | 删除手办 |
| GET | `/api/figures/export` | 导出手办 CSV |
| POST | `/api/figures/import` | 导入手办 CSV |
| PUT | `/api/figures/{id}/price-info` | 修改手办市场价 |
| POST | `/api/figures/{id}/add-position` | 补仓操作 |
| POST | `/api/figures/{id}/update-price` | 更新手办价格 |

### 标签
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/figures/tags` | 获取所有标签 |
| POST | `/api/figures/tags` | 创建标签 |
| PUT | `/api/figures/tags/{id}` | 更新标签 |
| DELETE | `/api/figures/tags/{id}` | 删除标签 |

### 愿望清单
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/wishlist/` | 获取愿望清单列表 |
| POST | `/api/wishlist/` | 创建愿望清单项（支持 HPOI URL 自动抓取） |
| PUT | `/api/wishlist/{id}` | 更新愿望清单项 |
| DELETE | `/api/wishlist/{id}` | 删除愿望清单项 |
| GET | `/api/wishlist/scrape` | HPOI URL 抓取预览 |

### 订单
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/orders/` | 获取订单列表（分页） |
| GET | `/api/orders/{id}` | 获取订单详情 |
| GET | `/api/orders/unpaid-balance/` | 获取未付尾款总额 |
| POST | `/api/orders/` | 创建订单 |
| PUT | `/api/orders/{id}` | 更新订单 |
| DELETE | `/api/orders/{id}` | 删除订单 |
| GET | `/api/orders/{id}/payment-details` | 获取订单支付明细 |
| POST | `/api/orders/{id}/pay-balance` | 确认尾款支付 |

### 卖出订单
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/sold-orders/` | 获取卖出订单列表（分页） |
| GET | `/api/sold-orders/{id}` | 获取卖出订单详情 |
| POST | `/api/sold-orders/` | 创建卖出订单 |
| PUT | `/api/sold-orders/{id}` | 更新卖出订单 |
| DELETE | `/api/sold-orders/{id}` | 删除卖出订单 |
| POST | `/api/sold-orders/from-inventory` | 从库存创建卖出订单 |

### 交易记录
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/trade_records/buy-order/{id}` | 查看买入订单流水 |
| GET | `/api/trade_records/sell-order/{id}` | 查看卖出订单流水 |
| GET | `/api/trade_records/monthly-stats` | 本月交易统计 |
| GET | `/api/trade_records/bill-export` | 账单导出 |

### 市场
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/market/dashboard` | HPI 看板数据 |
| GET | `/api/market/hpi-history` | HPI 历史走势 |
| GET | `/api/market/hpi-components` | HPI 成分股明细 |
| GET | `/api/market/sector-ranking` | 板块涨幅排行 |
| GET | `/api/market/kline` | K线数据 |

### 资产
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/assets/dashboard` | 资产看板数据 |
| GET | `/api/assets/positions` | 持仓列表 |
| GET | `/api/assets/distribution` | 资产分布 |
| GET | `/api/assets/profit-analysis` | 利润分析 |
| GET | `/api/assets/holdings/filter` | 持仓筛选（分页） |
| GET | `/api/assets/holdings` | 库存手办列表（用于卖出选择） |
| GET | `/api/exchange-rates` | 汇率查询 |

### 收藏家
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/collector/dashboard` | 收藏家仪表盘 |
| GET/POST/PUT/DELETE | `/api/collector/cabinets` | 收藏柜管理 |
| GET/POST/PUT/DELETE | `/api/collector/manufacturers` | 本命厂商管理 |
| GET/POST | `/api/collector/ratings` | 手办评分 |
| GET | `/api/collector/share` | 分享主页 |
| GET | `/api/collector/privacy` | 隐私设置 |

### 首页
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/home/summary` | 首页汇总（投资天数/本月补款/持仓TOP5 等） |
| GET | `/api/home/activities` | 首页最近动态 |

## 前端页面

| 路径 | 页面 | 说明 |
|------|------|------|
| `/home` | 首页 | 投资天数/本月补款/持仓 TOP5/动态时间线 |
| `/login` | 登录 | 用户登录 |
| `/register` | 注册 | 新用户注册 |
| `/dashboard` | 仪表盘 | 双模式主面板（倒狗/收藏家） |
| `/figures` | 手办库 | 管理所有手办（带真实分页） |
| `/figures/:id` | 手办详情 | 单款手办完整信息（双栏视觉重构） |
| `/orders` | 尾款管理 | 买入订单管理（三步向导新增/编辑） |
| `/sold-orders` | 卖出订单 | 管理已出售手办 |
| `/wishlist` | 愿望清单 | HPOI 抓取 + 手动管理 |
| `/profile` | 个人中心 | 资料编辑 |
| `/share/:userId` | 分享主页 | 对外展示的收藏主页 |

## 环境变量

完整配置在项目根目录的 `.env` 文件中，可按需修改：

```env
# ===== 数据库 =====
MYSQL_ROOT_PASSWORD=root                 # MySQL root 密码
MYSQL_USER=admin                          # MySQL 用户名
MYSQL_PASSWORD=password                   # MySQL 密码
MYSQL_DATABASE=figurebox                  # 数据库名

# ===== 后端 =====
SECRET_KEY=your-secret-key-change-in-production   # JWT 密钥（生产环境务必修改）
DATABASE_URL=mysql+pymysql://admin:password@db:3306/figurebox

# ===== MinIO 对象存储 =====
MINIO_ROOT_USER=figurebox                 # MinIO root 用户名
MINIO_ROOT_PASSWORD=FigureBox@2024!       # MinIO root 密码
MINIO_ENDPOINT=minio:9000                 # 容器内部地址
MINIO_ACCESS_KEY=figurebox                # 访问 key
MINIO_SECRET_KEY=FigureBox@2024!          # 访问密钥
MINIO_BUCKET=figurebox-images             # 存储桶名

# ===== MinIO 外部访问 =====
MINIO_PUBLIC_ENDPOINT=http://localhost:28640   # 外部 API 地址
MINIO_PUBLIC_URL=http://localhost:28620/minio  # 前端访问地址
MINIO_SECURE=false                            # 是否 HTTPS
MINIO_REGION=us-east-1
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

1. **首次部署**时，容器启动脚本会自动执行 `migrations/` 目录下的所有迁移脚本，创建所需的表结构
2. **生产环境**请务必修改 `SECRET_KEY` 为安全的随机字符串（如 `openssl rand -hex 32`）
3. **图片上传限制**：最多 10 张，每张不超过 20MB，Nginx 已配置 250MB 上限
4. **登录状态**：JWT 有效期 60 分钟，有操作会自动续期
5. **汇率数据**：来源于中国外汇交易中心（工作日 09:25 发布），非工作日使用最近交易日数据，缓存 3 小时
6. **HPI 指数**：使用人民币计价，外币订单通过汇率转换后参与计算
7. **时区**：所有容器已设置 `TZ=Asia/Shanghai`，避免 UTC 时间偏差
8. **外部图片自动转存**：HPOI 等外部图床图片会在保存手办/愿望清单/厂商 Logo 时自动转存至 MinIO，避免图床失效
9. **字符校验**：手办名称、涂装、原画、作品出处等字段支持日文重复符号 々、中文直角引号「」、下划线 _、中间点 ·、全角感叹号 ！等特殊字符
10. **数据备份**：重要数据请定期备份 `mysql_data` 和 `minio_data` 两个 Docker 卷

## 许可证

GNU Affero General Public License v3.0
