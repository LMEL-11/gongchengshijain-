# 智慧房源探索平台 (Smart Property Exploration Platform)

基于 **Flask + Vue 3 + Three.js** 的全栈房源数据可视化与房价预测平台。

通过采集二手房数据，对房价进行分析与预测，并以 **3D 可视化** 的方式呈现各城市、各区域的房源与价格分布，帮助用户在购房、租房、投资与市场了解等方面做出更明智的决策；同时展示房屋周边的学校、医院、地铁等配套设施，辅助评估生活便利性。

---

## ✨ 功能特性

- **3D 房价地图**：基于 Three.js，将各行政区渲染为立体柱体，柱体高度与颜色映射区域均价，支持旋转、缩放、悬停查看、点击下钻。
- **全国大屏房源点**：大屏下钻到城市级后，可在区/县弹层中查看百度地图房源分布；右侧“地图房源”列表支持定位地图点，并通过“详情”进入房源详情页。
- **登录与权限控制**：用户/管理员统一登录，前端使用路由守卫保护页面，后端使用 JWT Bearer Token 区分普通用户与管理员权限。
- **管理员房源管理**：管理员可按省市区域筛选、新增、编辑、删除房源；新增成功后可直接点击“查看详情”跳转到展示页，形成“录入 → 展示”的闭环。
- **三级区域选择**：房源总览、房源探索、数据分析统一使用“省份 / 城市 / 区域”三级选择器；“区域”兼容行政区、商圈、片区等数据口径。
- **房源探索**：多条件筛选（省份 / 城市 / 区域 / 户型 / 总价区间 / 关键词）、排序、分页浏览，查看房源详情。
- **周边配套**：房源详情页展示从山东原始文本抽取的学校、医院、交通、商场、公园等区/商圈级配套标签。
- **交易属性**：详情页展示挂牌时间、交易权属、产权情况、抵押信息、核心卖点、小区介绍、户型介绍、交通出行；管理员录入的数据优先展示，山东原始 TSV 字段作为兜底。
- **数据分析**：各区均价排行、单价分布直方图、投资热点评分（ECharts）。
- **房价预测**：按用户选择的行政区/商圈惰性训练随机森林模型，样本不足时自动降级为该区域均值启发式估算。
- **数据导入与采集**：支持山东 `house_info.tsv` 清洗导入、SQLite → MySQL 迁移脚本，以及 Scrapy 链家数据采集工程。

## 🧱 技术栈

| 层 | 技术 |
|----|------|
| 后端 | Flask 3 · Flask-SQLAlchemy · Flask-CORS · PyJWT · scikit-learn · pandas |
| 数据库 | MySQL / PostgreSQL（默认 MySQL；未配置时自动回退到 SQLite） |
| 前端 | Vue 3 (Composition API) · Vite · Vue Router · Pinia · Element Plus · Axios |
| 可视化 | Three.js（3D 地图）· ECharts（统计图表） |

## 📁 目录结构

```
工程实践/
├── .venv/                  # Python 虚拟环境（本地，已忽略提交）
├── backend/                # Flask 后端
│   ├── app.py              # 应用工厂 + 入口
│   ├── run.py              # 开发服务器入口
│   ├── config.py           # 配置（读取 .env）
│   ├── extensions.py       # db 实例
│   ├── seed.py             # 生成合成演示数据
│   ├── import_shandong_house_info.py # 山东 house_info.tsv 清洗导入
│   ├── import_shandong_facilities.py # 从山东原始文本抽取配套设施标签
│   ├── migrate_sqlite_to_mysql.py    # SQLite 数据迁移到 MySQL
│   ├── requirements.txt
│   ├── .env.example        # 环境变量模板（数据库连接等）
│   ├── data/
│   │   ├── province_data.csv
│   │   └── raw/            # house_info.tsv / house_info.sql 原始数据
│   ├── seed_users.py       # 创建默认 user/admin 演示账户
│   ├── models/             # ORM 模型：城市/区/房源/交易属性/用户/设施/价格走势
│   ├── api/                # 蓝图路由：auth/admin/cities/districts/properties/stats/facilities/national
│   ├── services/           # 业务逻辑：analysis（统计）/ prediction（预测）
│   └── spider/             # 数据采集骨架（含合规说明）
├── crawler/                 # Scrapy 链家爬虫工程
└── frontend/               # Vue 3 前端
    ├── vite.config.js      # 含 /api -> :5000 代理
    └── src/
        ├── views/          # Screen / Login / Dashboard / Explore / PropertyDetail / Analysis / Admin
        ├── components/     # RegionSelector / CityMap3D（Three.js）/ 图表 / 预测表单 / 卡片
        ├── api/            # axios 封装与接口定义
        ├── store/          # Pinia 状态
        └── router/
```

---

## 🚀 快速开始

### 0. 环境要求

- Python 3.9+，Node.js 18+（已在 Node 24 / Python 3.9 验证）
- （可选）MySQL 或 PostgreSQL

### 1. 后端

```bash
# 1) 激活项目根目录下的虚拟环境
source .venv/bin/activate

# 2) 安装依赖（首次）
pip install -r backend/requirements.txt

# 3) 配置数据库连接（当前项目默认使用 MySQL）
cp backend/.env.example backend/.env
#   编辑 backend/.env，填入 DATABASE_URL。
#   MySQL 需先创建库：
#   mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS housing DEFAULT CHARACTER SET utf8mb4;"

# 4) 如是新库或缺少登录账户，创建课程演示用默认账户
cd backend
../.venv/bin/python -m flask --app app seed-users

# 5) 启动后端（默认 http://127.0.0.1:5000）
../.venv/bin/python run.py
```

默认演示账户：管理员 `admin / admin123`，普通用户 `user / user123`。正式演示或部署前请修改默认密码。

当前开发数据已在 MySQL 中。如需重新导入山东原始数据，可执行：

```bash
cd /Users/lme/study/project/工程实践/backend
env PYTHONDONTWRITEBYTECODE=1 ../.venv/bin/python import_shandong_house_info.py --file data/raw/house_info.tsv --replace
env PYTHONDONTWRITEBYTECODE=1 ../.venv/bin/python import_shandong_facilities.py --file data/raw/house_info.tsv --replace
```

如只是需要合成演示数据，可运行 `../.venv/bin/python -m flask --app app seed`，但这不是当前项目展示数据的推荐流程。

### 2. 前端

```bash
cd frontend
npm install                  # 首次
# 如需在大屏市级区县页显示百度地图房源点：
# cp .env.example .env.local
# 然后在 .env.local 填入 VITE_BAIDU_MAP_AK
npm run dev                  # 启动开发服务器 http://localhost:5173
```

浏览器打开 **http://localhost:5173** 后会先进入登录页。登录后，普通用户可访问数据大屏、房源总览、房源探索、数据分析和详情页；管理员可额外进入 `/admin` 管理后台。前端通过 Vite 代理把 `/api` 请求转发到 `http://127.0.0.1:5000`，无需额外处理跨域。

大屏地图使用路径：进入首页 `/`，按“全国 → 省 → 市”下钻；到城市级后点击区/县会打开百度地图房源弹层。弹层左侧地图展示点位，右侧“地图房源”列表点击房源内容可定位 marker，点击“详情”会跳转到 `/property/{id}` 房源详情页。

生产构建：`npm run build`（产物在 `frontend/dist/`）。

---

## 🔌 API 一览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| POST | `/api/auth/login` | 用户/管理员登录，返回 JWT 与用户信息 |
| GET | `/api/auth/me` | 根据 JWT 获取当前用户 |
| POST | `/api/auth/logout` | 退出登录（客户端丢弃 token） |
| GET | `/api/cities` | 城市列表 |
| GET | `/api/cities/{id}/districts` | 某城市各区（含均价，按价排序，供 3D 地图） |
| GET | `/api/districts/{id}/facilities` | 某区周边配套设施 |
| GET | `/api/districts/{id}/price-trend` | 某区房价走势 |
| GET | `/api/properties` | 房源列表（筛选/排序/分页） |
| GET | `/api/properties/{id}` | 房源详情（含周边设施与交易属性；管理员录入优先、山东原始字段兜底） |
| GET | `/api/stats/overview` | 平台总览统计 |
| GET | `/api/stats/district-ranking?city_id=` | 各区均价排行 |
| GET | `/api/stats/price-distribution?city_id=` | 单价分布直方图 |
| GET | `/api/stats/investment?city_id=` | 各区投资评分排行 |
| GET | `/api/stats/price-trend?district_id=` | 房价走势 |
| GET | `/api/stats/listing-profile?district_id=` | 区域挂牌画像（挂牌月份、均价、交易属性结构） |
| POST | `/api/stats/predict` | 房价预测（body 见下） |
| POST | `/api/stats/predict/retrain` | 强制重训模型（可传 `district_id`） |
| GET | `/api/admin/properties` | 管理员房源列表（支持关键词、区域、分页） |
| GET | `/api/admin/properties/{id}` | 管理员查看房源详情 |
| POST | `/api/admin/properties` | 管理员新增房源及交易属性 |
| PUT | `/api/admin/properties/{id}` | 管理员编辑房源及交易属性 |
| DELETE | `/api/admin/properties/{id}` | 管理员删除房源 |
| GET | `/api/national/real/summary` | 当前真实库总览 |
| GET | `/api/national/real/provinces` | 省级真实房源聚合 |
| GET | `/api/national/real/cities?province=` | 某省城市真实房源聚合 |
| GET | `/api/national/real/districts?city=` | 某市行政区/商圈真实房源聚合 |
| GET | `/api/national/real/area-properties?city=&area=&limit=` | 某市某区县可定位房源点（大屏内嵌百度地图；返回项含房源 `id`，用于跳转详情） |

**房源筛选参数**：`city_id, district_id, listing_type, rooms, keyword, min_total_price, max_total_price, min_unit_price, max_unit_price, sort(price_asc|price_desc|unit_asc|unit_desc|area_desc|newest), page, page_size`

**预测请求体示例**：

```json
{ "district_id": 3, "area": 90, "rooms": 2, "halls": 1,
  "build_year": 2015, "has_elevator": true, "floor": 10, "total_floors": 18 }
```

---

## 🕷 数据采集（爬虫）

`backend/spider/` 提供轻量采集骨架；`crawler/` 是 Scrapy 链家爬虫工程，用于把链家列表页快照写入当前后端数据库。真实采集前请先阅读 `crawler/README.md`，遵守目标网站 robots.txt 与服务条款，控制频率，不绕过登录、验证码或反爬限制。

```bash
cd backend
python -m spider.example_spider   # 演示：解析示例 HTML 并入库
```

山东批量数据已经以 `backend/data/raw/house_info.tsv` 为原始文件导入，`backend/data/raw/house_info.sql` 保留作原始备份/核对。

---

## 📝 说明

- 当前 MySQL 数据规模：**126002 条房源 / 139 城 / 2488 个区或商圈**，其中 `shandong_house_info` 121617 条、`lianjia` 4385 条。
- 山东原始数据以商圈字段入库，大屏市级下钻会根据 `house_info.tsv` 中 `region/quyu` 映射，把商圈房源数汇总到行政区；区/县/市后缀做了规范化，并保护 `单县`、`曹县` 这类名称不被误截断。
- 大屏下钻到城市级后，点击区/县会在当前大屏内显示百度地图房源点；右侧列表可点击“详情”进入对应房源详情页；需在 `frontend/.env.local` 配置 `VITE_BAIDU_MAP_AK`。
- 房源总览、房源探索、数据分析的区域选择统一由 `RegionSelector.vue` 实现，第三层命名为“区域”，用于兼容行政区、商圈、片区等不同数据粒度。
- 管理后台新增/编辑房源会同时维护 `properties` 与 `property_transactions`；普通详情接口优先展示管理员维护的交易属性，若没有则回退到山东原始 TSV 字段。
- 周边配套不是逐房源 POI 坐标，而是由山东 `maidian/jieshao/huxingjieshao/jiaotong` 文本抽取后按区/商圈汇总的设施标签，目前写入 `facilities` 表 4513 条。
- 山东房源详情的原始交易属性由 `services/property_details.py` 按 `source_url` 从原始 TSV 查询；管理员录入的交易属性保存在 `property_transactions` 表。
- 投资热点评分已改为当前快照可支撑的五项指标：价格洼地 35%、市场热度 25%、周边配套 20%、交易安全 10%、挂牌新鲜度 10%，不再使用无法确认的近期涨幅。
- 房价预测模型在首次调用 `/api/stats/predict` 时按所选 `district_id` 惰性训练并缓存；样本少于 30 条或无 sklearn 时使用该行政区/商圈均值兜底。
