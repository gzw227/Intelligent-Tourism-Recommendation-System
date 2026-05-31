# 智游中国 — 智能旅游推荐系统

## 一、项目概述

本系统是一个基于中国城市景点数据的智能旅游推荐系统，采用前后端分离的四层分层架构。系统从345个城市、30791个景点的真实数据集出发，结合ItemCF协同过滤与DeepFM深度学习两种推荐算法，为用户提供个性化旅游推荐服务。

### 核心特性

| 特性 | 说明 |
|------|------|
| 数据规模 | 352个城市、30791个景点 |
| 推荐算法 | ItemCF协同过滤 + DeepFM深度学习（混合权重 0.4:0.6） |
| 冷启动策略 | 无行为数据时自动回退到热门推荐 |
| 前端技术 | Vue3 + Element Plus（CDN模式，无需Node.js） |
| 后端技术 | FastAPI + SQLAlchemy + SQLite |
| 算法框架 | PyTorch + scikit-learn |

---

## 二、系统架构

### 2.1 架构说明

系统采用前后端分离的四层分层架构，各层职责明确、耦合度低：

```
┌──────────────────────────────────────────────────────┐
│              前端展示层 (Vue3 + Element Plus)           │
│   登录注册 / 首页推荐 / 景点详情 / 景点浏览 / 个人中心    │
├──────────────────────────────────────────────────────┤
│              后端服务层 (FastAPI)                       │
│   用户服务 / 景点服务 / 行为服务 / 推荐服务 / 模型服务     │
├──────────────────────────────────────────────────────┤
│              算法模型层                                 │
│   ItemCF协同过滤 / DeepFM深度学习 / 混合推荐器           │
├──────────────────────────────────────────────────────┤
│              数据持久层 (SQLite)                        │
│   users / attractions / user_behaviors                │
└──────────────────────────────────────────────────────┘
```

- **前端展示层**：负责用户交互与页面渲染，提供登录注册、首页推荐、景点详情、景点浏览、个人中心（收藏/浏览历史）页面。
- **后端服务层**：提供RESTful接口，包含用户、景点、行为、推荐、模型调用五大服务，对接前端、算法层与数据库。
- **算法模型层**：实现两类推荐算法，传统算法选用ItemCF（景点协同过滤），深度学习算法选用DeepFM；完成模型训练、保存、加载与推理，返回个性化推荐结果。
- **数据持久层**：存储用户信息、景点数据、用户行为记录，支撑系统业务与算法训练。

### 2.2 系统流程

```
用户登录 → 浏览/收藏景点 → 行为记录写入数据库
    ↓
请求推荐 → 后端读取用户历史行为
    ↓
同时调用 ItemCF 与 DeepFM 模型
    ↓
合并排序 (0.4×ItemCF + 0.6×DeepFM)
    ↓
返回 Top-N 推荐结果 → 前端渲染展示
```

1. 用户登录：验证身份，获取用户ID与Token
2. 用户交互：浏览景点、收藏景点，产生行为数据
3. 行为记录：后端将用户行为写入数据库，为推荐算法提供数据
4. 推荐调用：后端请求算法层，同时调用ItemCF与DeepFM模型
5. 结果融合：将两种算法的推荐结果合并、去重、排序，生成最终推荐列表
6. 结果展示：前端将推荐结果渲染到首页，供用户查看

---

## 三、项目目录结构

```
recommend travel system/
├── backend/                              # 后端服务层
│   ├── main.py                           # FastAPI应用入口（路由注册、模型加载、前端页面服务）
│   ├── database.py                       # 数据库连接（SQLAlchemy + SQLite）
│   ├── models.py                         # ORM模型定义（User / Attraction / UserBehavior）
│   ├── init_db.py                        # 数据库初始化脚本（建表 + CSV数据导入）
│   ├── templates/
│   │   └── index.html                    # 前端单页面（Vue3 CDN模式，无需Node.js）
│   ├── routers/                          # API路由模块
│   │   ├── user.py                       # 用户服务（注册/登录/信息查询与修改）
│   │   ├── attraction.py                 # 景点服务（列表/详情/城市/搜索）
│   │   ├── behavior.py                   # 行为服务（浏览记录/收藏/取消收藏/历史查询）
│   │   ├── recommend.py                  # 推荐服务（个性化/热门/相似/季节推荐）
│   │   └── model.py                      # 模型服务（训练触发/状态查询/模型重载）
│   └── services/
│       └── recommend_service.py          # 推荐业务逻辑（混合推荐 + 冷启动回退）
├── algorithms/                           # 算法模型层
│   ├── item_cf.py                        # ItemCF协同过滤算法
│   ├── deepfm.py                         # DeepFM深度学习模型（PyTorch）
│   ├── hybrid_recommender.py             # 混合推荐器（0.4×ItemCF + 0.6×DeepFM）
│   ├── train.py                          # 模型训练脚本
│   └── models/                           # 训练好的模型文件存储目录
│       └── .gitkeep
├── frontend/                             # Vue3前端源码（需Node.js环境，可选）
│   ├── src/
│   │   ├── App.vue                       # 根组件
│   │   ├── main.js                       # Vue3入口
│   │   ├── router/index.js               # 路由配置
│   │   ├── stores/user.js                # Pinia用户状态管理
│   │   ├── utils/request.js              # Axios请求封装
│   │   ├── views/
│   │   │   ├── Home.vue                  # 首页
│   │   │   ├── Login.vue                 # 登录页
│   │   │   ├── Register.vue              # 注册页
│   │   │   ├── AttractionList.vue        # 景点浏览页
│   │   │   ├── AttractionDetail.vue      # 景点详情页
│   │   │   └── Profile.vue               # 个人中心页
│   │   ├── components/
│   │   │   └── AttractionCard.vue        # 景点卡片组件
│   │   └── styles/global.css             # 全局样式
│   ├── package.json
│   └── vite.config.js
├── china-city-attraction-details/        # 数据集目录
│   └── citydata/                         # 352个城市CSV文件
│       ├── 北京.csv
│       ├── 上海.csv
│       └── ...
├── travel_recommend.db                   # SQLite数据库文件（运行后自动生成）
├── requirements.txt                      # Python依赖
└── start.bat                             # Windows启动脚本
```

---

## 四、环境配置

### 4.1 系统要求

| 项目 | 最低要求 | 推荐配置 |
|------|---------|---------|
| 操作系统 | Windows 10 / macOS / Linux | Windows 11 |
| Python | 3.8+ | 3.11 |
| 内存 | 4GB | 8GB+ |
| 磁盘空间 | 2GB | 5GB+ |
| Node.js | 可选（仅Vue3开发模式需要） | 18+ |

### 4.2 Python环境配置

#### 方式一：系统Python直接安装

```bash
# 1. 确认Python版本
python --version    # 需要 3.8+

# 2. 安装后端依赖
pip install -r requirements.txt
```

#### 方式二：使用虚拟环境（推荐）

```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt
```

### 4.3 Python依赖清单

| 包名 | 版本 | 用途 |
|------|------|------|
| fastapi | 0.104.1 | Web框架 |
| uvicorn | 0.24.0 | ASGI服务器 |
| sqlalchemy | 2.0.23 | ORM框架 |
| pydantic | 2.5.2 | 数据校验 |
| torch | 2.1.0 | DeepFM深度学习模型 |
| numpy | 1.24.3 | 数值计算 |
| scikit-learn | 1.3.2 | 机器学习工具 |
| pymysql | 1.1.0 | MySQL连接器（训练脚本用） |
| cryptography | 41.0.7 | 加密支持 |

> **说明**：当前系统使用SQLite作为默认数据库，无需安装MySQL即可运行。训练脚本`train.py`中使用pymysql连接MySQL，如需训练模型请安装MySQL或修改训练脚本适配SQLite。

### 4.4 Node.js环境配置（可选）

仅在使用Vue3开发模式（frontend目录）时需要：

```bash
# 1. 安装Node.js（从 https://nodejs.org 下载）

# 2. 进入前端目录
cd frontend

# 3. 安装前端依赖
npm install

# 4. 启动开发服务器
npm run dev
```

前端依赖清单：

| 包名 | 版本 | 用途 |
|------|------|------|
| vue | ^3.4.0 | 前端框架 |
| vue-router | ^4.3.0 | 路由管理 |
| element-plus | ^2.7.0 | UI组件库 |
| @element-plus/icons-vue | ^2.3.0 | 图标库 |
| axios | ^1.7.0 | HTTP请求 |
| pinia | ^2.1.0 | 状态管理 |
| vite | ^5.4.0 | 构建工具 |
| @vitejs/plugin-vue | ^5.0.0 | Vue插件 |

> **说明**：系统已内置CDN模式的前端页面（`backend/templates/index.html`），无需Node.js即可直接通过浏览器访问。Vue3源码（frontend目录）仅用于开发调试。

### 4.5 数据库配置

系统默认使用**SQLite**数据库，无需额外安装和配置。数据库文件`travel_recommend.db`在首次运行初始化脚本时自动生成。

如需切换为MySQL，修改`backend/database.py`：

```python
# SQLite（默认）
DATABASE_URL = "sqlite:///./travel_recommend.db"

# MySQL（需安装MySQL并创建数据库）
DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/travel_recommend?charset=utf8mb4"
```

MySQL建库命令：

```sql
CREATE DATABASE IF NOT EXISTS travel_recommend DEFAULT CHARSET utf8mb4;
```

---

## 五、快速启动

### 5.1 一键启动（推荐）

```bash
# 1. 安装Python依赖
pip install -r requirements.txt

# 2. 初始化数据库（建表 + 导入352个城市30791个景点数据）
python -m backend.init_db

# 3. 启动后端服务
python -m backend.main

# 4. 浏览器访问
# http://localhost:8000
```

### 5.2 分步启动

#### 步骤1：初始化数据库

```bash
python -m backend.init_db
```

输出示例：

```
Tables created successfully.
Found 352 CSV files.
[50/352] Parsed 3927 attractions so far...
[100/352] Parsed 8096 attractions so far...
...
[352/352] Parsed 30791 attractions so far...
Total parsed: 30791 attractions from 352 cities
Inserting into database (this may take a moment)...
  Inserted batch 1: 500 records
  ...
  Inserted batch 62: 291 records
Done! Total inserted: 30791
```

#### 步骤2：训练推荐模型（需要用户行为数据）

```bash
python -m algorithms.train
```

> **注意**：模型训练需要数据库中存在用户行为数据。系统在无模型时自动使用热门推荐作为冷启动回退策略。建议先让用户产生浏览和收藏行为后再训练模型。

也可通过API触发训练：

```bash
curl -X POST http://localhost:8000/api/model/train
```

#### 步骤3：启动后端服务

```bash
python -m backend.main
```

输出：

```
INFO:     Started server process [xxxx]
INFO:     Waiting for application startup.
Warning: Failed to load models: ...  # 首次启动无模型文件，属正常现象
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

#### 步骤4：访问系统

- 前端页面：http://localhost:8000
- API文档：http://localhost:8000/docs

---

## 六、数据库设计

### 6.1 ER关系图

```
┌──────────────┐       ┌──────────────────┐       ┌──────────────┐
│    users     │       │  user_behaviors   │       │ attractions  │
├──────────────┤       ├──────────────────┤       ├──────────────┤
│ id (PK)      │──┐    │ id (PK)          │    ┌──│ id (PK)      │
│ username     │  └───>│ user_id (FK)     │    │  │ name         │
│ password     │       │ attraction_id(FK)│<───┘  │ city         │
│ nickname     │       │ behavior_type    │       │ address      │
│ avatar       │       │ created_at       │       │ description  │
│ created_at   │       └──────────────────┘       │ open_time    │
└──────────────┘                                  │ image_url    │
                                                  │ rating       │
                                                  │ play_time    │
                                                  │ season       │
                                                  │ ticket       │
                                                  │ tips         │
                                                  │ source_url   │
                                                  └──────────────┘
```

### 6.2 表结构详细设计

#### users 表（用户表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, 自增 | 用户ID |
| username | String(50) | 唯一, 非空 | 用户名 |
| password | String(255) | 非空 | 密码（SHA-256哈希） |
| nickname | String(50) | | 昵称 |
| avatar | String(255) | | 头像URL |
| created_at | DateTime | 默认当前时间 | 注册时间 |

#### attractions 表（景点表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, 自增 | 景点ID |
| name | String(200) | 非空 | 景点名称 |
| city | String(50) | 非空 | 所在城市 |
| address | Text | | 详细地址 |
| description | Text | | 景点介绍 |
| open_time | String(255) | | 开放时间 |
| image_url | String(500) | | 图片链接 |
| rating | Float | 默认0 | 评分（0-5） |
| play_time | String(100) | | 建议游玩时间 |
| season | String(100) | | 建议季节 |
| ticket | Text | | 门票信息 |
| tips | Text | | 小贴士 |
| source_url | String(500) | | 数据来源链接 |

#### user_behaviors 表（用户行为表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, 自增 | 行为ID |
| user_id | Integer | FK→users.id, 非空 | 用户ID |
| attraction_id | Integer | FK→attractions.id, 非空 | 景点ID |
| behavior_type | String(20) | 非空 | 行为类型：browse（浏览）/ collect（收藏） |
| created_at | DateTime | 默认当前时间 | 行为时间 |

---

## 七、API接口文档

所有接口统一返回格式：

```json
{
    "code": 200,
    "message": "操作成功",
    "data": {}
}
```

### 7.1 用户服务 `/api/user`

| 方法 | 路径 | 说明 | 请求参数 |
|------|------|------|---------|
| POST | `/api/user/register` | 用户注册 | `{username, password, nickname}` |
| POST | `/api/user/login` | 用户登录 | `{username, password}` |
| GET | `/api/user/info/{user_id}` | 获取用户信息 | 路径参数：user_id |
| PUT | `/api/user/info/{user_id}` | 更新用户信息 | `{nickname?, avatar?}` |

**注册示例**：

```bash
curl -X POST http://localhost:8000/api/user/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"123456","nickname":"测试用户"}'
```

**登录示例**：

```bash
curl -X POST http://localhost:8000/api/user/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"123456"}'
```

返回：

```json
{
    "code": 200,
    "message": "登录成功",
    "data": {
        "user_id": 1,
        "username": "test",
        "nickname": "测试用户",
        "token": "a1b2c3d4e5f6..."
    }
}
```

### 7.2 景点服务 `/api/attractions`

| 方法 | 路径 | 说明 | 请求参数 |
|------|------|------|---------|
| GET | `/api/attractions/list` | 景点列表（分页） | `page, page_size, city?, keyword?, min_rating?` |
| GET | `/api/attractions/detail/{id}` | 景点详情 | 路径参数：景点ID |
| GET | `/api/attractions/cities` | 获取所有城市 | 无 |
| GET | `/api/attractions/search` | 搜索景点 | `keyword, page, page_size` |

**景点列表示例**：

```bash
curl "http://localhost:8000/api/attractions/list?page=1&page_size=12&city=北京&min_rating=4"
```

### 7.3 行为服务 `/api/behavior`

| 方法 | 路径 | 说明 | 请求参数 |
|------|------|------|---------|
| POST | `/api/behavior/browse` | 记录浏览 | `{user_id, attraction_id}` |
| POST | `/api/behavior/collect` | 收藏景点 | `{user_id, attraction_id}` |
| DELETE | `/api/behavior/collect` | 取消收藏 | `{user_id, attraction_id}` |
| GET | `/api/behavior/collects/{user_id}` | 收藏列表 | `page, page_size` |
| GET | `/api/behavior/history/{user_id}` | 浏览历史 | `page, page_size` |
| GET | `/api/behavior/is_collected` | 是否已收藏 | `user_id, attraction_id` |

### 7.4 推荐服务 `/api/recommend`

| 方法 | 路径 | 说明 | 请求参数 |
|------|------|------|---------|
| GET | `/api/recommend/personal/{user_id}` | 个性化推荐 | `top_n` |
| GET | `/api/recommend/popular` | 热门推荐 | `top_n` |
| GET | `/api/recommend/similar/{attraction_id}` | 相似景点 | `top_n` |
| GET | `/api/recommend/seasonal` | 季节推荐 | `season, top_n` |

**个性化推荐示例**：

```bash
curl "http://localhost:8000/api/recommend/personal/1?top_n=12"
```

返回：

```json
{
    "code": 200,
    "message": "获取个性化推荐成功",
    "data": [
        {
            "attraction": {
                "id": 11,
                "name": "波罗森林公园",
                "city": "七台河",
                "rating": 5.0,
                ...
            },
            "score": 0.85
        }
    ]
}
```

### 7.5 模型服务 `/api/model`

| 方法 | 路径 | 说明 | 请求参数 |
|------|------|------|---------|
| POST | `/api/model/train` | 触发模型训练 | 无 |
| GET | `/api/model/status` | 查询模型状态 | 无 |
| POST | `/api/model/reload` | 重新加载模型 | 无 |

---

## 八、算法模型层

### 8.1 ItemCF协同过滤

**文件**：`algorithms/item_cf.py`

**原理**：基于物品的协同过滤算法，通过计算景点之间的相似度来推荐。如果两个景点被同一用户交互过，则认为它们相似。

**算法流程**：

1. 构建用户-景点交互矩阵，行为权重：浏览=1.0，收藏=2.0，评分=3.0
2. 计算景点间余弦相似度
3. 每个景点保留Top-50个最相似景点
4. 推荐时：找到用户交互过的景点 → 扩展到相似景点 → 聚合得分 → 排序返回

**核心代码**：

```python
from algorithms.item_cf import ItemCF

model = ItemCF()
model.train(behaviors)           # behaviors: [(user_id, attraction_id, behavior_type), ...]
results = model.recommend(user_id, behaviors, top_n=10)  # 返回: [(attraction_id, score), ...]
model.save("item_cf.pkl")        # 保存模型
model.load("item_cf.pkl")        # 加载模型
```

### 8.2 DeepFM深度学习

**文件**：`algorithms/deepfm.py`

**原理**：DeepFM结合了FM（因子分解机）和DNN（深度神经网络）的优势，能够同时学习特征之间的低阶交叉和高阶交叉。

**模型结构**：

```
输入: sparse_inputs = {user_id, attraction_id, city, season, rating_level}
  │
  ├── FM一阶部分: Embedding → Linear
  ├── FM二阶部分: Embedding → 两两内积交互
  └── Deep部分: Embedding拼接 → MLP(64→32) → Linear
  │
  输出: sigmoid(FM一阶 + FM二阶 + Deep)
```

**模型参数**：

| 参数 | 值 | 说明 |
|------|------|------|
| embedding_dim | 16 | 嵌入维度 |
| hidden_dims | [64, 32] | MLP隐藏层维度 |
| dropout | 0.3 | Dropout率 |
| optimizer | Adam | 优化器 |
| learning_rate | 0.001 | 学习率 |
| loss | BCELoss | 损失函数 |
| epochs | 20 | 训练轮数 |
| batch_size | 256 | 批次大小 |

**特征说明**：

| 特征名 | 说明 | 编码方式 |
|--------|------|---------|
| user_id | 用户ID | 整数索引编码 |
| attraction_id | 景点ID | 整数索引编码 |
| city | 城市名 | 整数索引编码 |
| season | 建议季节 | 整数索引编码 |
| rating_level | 评分等级(0-5) | 分箱编码 |

### 8.3 混合推荐器

**文件**：`algorithms/hybrid_recommender.py`

**融合策略**：

```
最终得分 = 0.4 × ItemCF得分 + 0.6 × DeepFM得分
```

- ItemCF擅长捕捉用户行为模式中的相似性
- DeepFM擅长学习特征之间的交叉关系
- 混合策略取长补短，提升推荐质量

### 8.4 冷启动策略

当用户没有历史行为数据时，系统自动回退到热门推荐（按评分排序的Top-N景点），确保新用户也能获得有价值的推荐。

---

## 九、前端页面说明

### 9.1 页面列表

| 页面 | 路由 | 说明 |
|------|------|------|
| 首页 | `/` | 英雄搜索区、热门城市、热门景点、当季推荐 |
| 景点浏览 | `/` (切换标签) | 城市筛选、评分筛选、关键词搜索、分页 |
| 景点详情 | 弹窗 | 景点信息、收藏、相似推荐 |
| 登录 | 弹窗 | 用户名+密码登录 |
| 注册 | 弹窗 | 用户名+密码+昵称注册 |
| 个人中心 | `/` (切换标签) | 我的收藏、浏览历史 |

### 9.2 两种前端模式

| 模式 | 文件位置 | 是否需要Node.js | 说明 |
|------|---------|----------------|------|
| CDN模式 | `backend/templates/index.html` | 否 | 通过CDN加载Vue3和Element Plus，直接由FastAPI提供服务 |
| 开发模式 | `frontend/` 目录 | 是 | 使用Vite构建，支持热更新，适合开发调试 |

**CDN模式**（默认）：

- 访问 http://localhost:8000 直接使用
- 无需安装Node.js
- Vue3、Element Plus、Axios通过unpkg CDN加载

**开发模式**：

```bash
cd frontend
npm install
npm run dev    # 启动 http://localhost:3000
```

需要在`frontend/vite.config.js`中配置API代理到后端8000端口。

---

## 十、数据集说明

### 10.1 数据来源

数据来源于去哪儿网（qunar.com），涵盖中国352个城市的旅游景点信息。

### 10.2 数据格式

每个城市一个CSV文件，文件名为城市名（如`北京.csv`），包含以下12个字段：

| 列名 | 类型 | 说明 | 示例 |
|------|------|------|------|
| 名字 | 字符串 | 景点名称（中英文） | 故宫博物院 The Palace Museum |
| 链接 | URL | 去哪儿网页链接 | http://travel.qunar.com/p-oi... |
| 地址 | 文本 | 详细地址（含电话、官网） | 北京市东城区景山前街4号 |
| 介绍 | 长文本 | 景点详细描述 | 故宫博物院是在明朝... |
| 开放时间 | 字符串 | 开放时间 | 全年 08:30-17:00 |
| 图片链接 | URL | 景点图片 | https://tr-osdcp.qunarzz.com/... |
| 评分 | 浮点数 | 景点评分 | 4.8 |
| 建议游玩时间 | 字符串 | 建议游览时长 | 建议游览时间：3小时 - 4小时 |
| 建议季节 | 字符串 | 推荐季节 | 春秋两季 |
| 门票 | 字典字符串 | 门票价格 | {'成人票': ['¥60起'], ...} |
| 小贴士 | 文本 | 游玩注意事项 | 建议提前网上购票... |
| Page | 整数 | 页码 | 1 |

### 10.3 数据特点

- 部分景点存在字段缺失（评分、介绍、季节等可能为空）
- 地址和介绍字段包含多行文本，CSV中用双引号包裹
- 门票字段以Python字典格式存储
- 热门景点信息较完整，冷门景点缺失较多

---

## 十一、常见问题

### Q1：首次启动报错 `ModuleNotFoundError`

```bash
# 确保在项目根目录下安装依赖
cd "d:\智能旅游推荐系统\recommend travel system"
pip install -r requirements.txt
```

### Q2：数据库初始化很慢

`init_db.py`已优化为批量插入模式，352个CSV文件约需1-2分钟。如仍觉得慢，可在`init_db.py`中减少导入的城市数量。

### Q3：模型加载失败

首次启动时没有训练好的模型文件，系统会输出Warning并自动使用热门推荐作为回退策略，不影响正常使用。待用户产生行为数据后，通过API或训练脚本训练模型即可。

### Q4：前端页面无法加载CDN资源

系统通过unpkg CDN加载Vue3和Element Plus，需要网络连接。如在内网环境，可将CDN资源下载到本地。

### Q5：如何切换MySQL数据库

1. 安装MySQL并创建数据库
2. 修改`backend/database.py`中的`DATABASE_URL`
3. 修改`algorithms/train.py`中的`DB_CONFIG`
4. 重新运行`python -m backend.init_db`

### Q6：如何训练模型

```bash
# 方式1：命令行训练（需MySQL）
python -m algorithms.train

# 方式2：API触发训练
curl -X POST http://localhost:8000/api/model/train
```

训练需要数据库中存在用户行为数据（浏览和收藏记录）。建议先让多个用户浏览和收藏景点后再训练。

---

## 十二、技术栈汇总

| 层次 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 前端 | Vue3 | 3.4.x | 响应式UI框架 |
| 前端 | Element Plus | 2.7.x | UI组件库 |
| 前端 | Axios | 1.7.x | HTTP请求 |
| 前端 | Pinia | 2.1.x | 状态管理 |
| 后端 | FastAPI | 0.104.x | Web框架 |
| 后端 | Uvicorn | 0.24.x | ASGI服务器 |
| 后端 | SQLAlchemy | 2.0.x | ORM框架 |
| 后端 | Pydantic | 2.5.x | 数据校验 |
| 算法 | PyTorch | 2.1.x | DeepFM模型 |
| 算法 | NumPy | 1.24.x | 数值计算 |
| 算法 | scikit-learn | 1.3.x | TF-IDF向量化 |
| 数据库 | SQLite | 内置 | 数据持久化 |
| 构建 | Vite | 5.4.x | 前端构建工具 |
