# 链家二手房爬虫（Scrapy）

基于 **Scrapy** 的二手房信息采集器，抓取**链家（lianjia.com）**二手房**列表页**
（列表页已含 户型/面积/朝向/装修/楼层/总价/单价/小区/区域），清洗后**直接写入后端数据库**
（`Property` 表），前端「房源探索」页即可展示真实数据。

> 链家**详情页有验证码反爬**，默认不访问；如确有授权可 `-a follow_detail=1` 跟进详情页补充
> 楼层/经纬度（多半会被验证码拦截，本爬虫不做任何绕过）。

> ⚠️ **合规与道德使用**：本爬虫仅用于课程学习/演示。已内置 `robots.txt` 遵守、低并发、
> 下载延迟、AutoThrottle 与抓取数量安全阀，**不绕过任何反爬**（不破解验证码、不模拟登录、
> 不轮换代理规避封禁）。使用前请确认你**有权**抓取目标站，并遵守其服务条款（ToS）。
> 真实站点常有反爬，抓取可能被限流或返回验证页——这属正常现象，请勿试图绕过。

> 🔎 **实测（2026-06-03）**：链家 `robots.txt` **禁止 `/ershoufang/`**，因此默认
> `ROBOTSTXT_OBEY=True` 时不会抓取（返回 0 条）。若你**已获授权**用于课程用途，可对单次运行
> 追加 `-s ROBOTSTXT_OBEY=False` 覆盖——这表示你自行承担越过该站爬取策略的责任。

---

## 目录结构

```
crawler/
├── scrapy.cfg                       # Scrapy 项目入口
├── requirements.txt                 # 依赖（Scrapy）
├── run_crawl.py                     # 便捷启动脚本
└── housing_crawler/
    ├── settings.py                  # 合规/限速/管道配置
    ├── items.py                     # HousingItem（字段对应 Property 模型）
    ├── pipelines.py                 # 清洗校验 + 写入数据库
    └── spiders/
        └── lianjia.py               # 链家二手房 Spider
```

## 1. 安装依赖

把 Scrapy 装进**项目根目录的同一个 `.venv`**（这样管道才能 import 后端的 Flask/SQLAlchemy）：

```bash
cd /Users/mjt/Desktop/工程实践
source .venv/bin/activate                 # Windows: .venv\Scripts\Activate.ps1
pip install -r crawler/requirements.txt   # 慢可加 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 2. 运行

```bash
cd crawler

# 链家 robots 禁止 /ershoufang/；如已获授权用于课程用途，追加 -s ROBOTSTXT_OBEY=False
scrapy crawl lianjia -a city=bj -a city_name=北京 -a max_pages=5 -s ROBOTSTXT_OBEY=False

# 便捷脚本（默认遵守 robots；需覆盖时建议用上面的 scrapy 命令）
python run_crawl.py bj 北京 5

# 指定城市内某板块/区（region 用链家 URL 里的拼音），并取消 200 条安全阀：
scrapy crawl lianjia -a city=jn -a city_name=济南 -a region=lixiaqu -a max_pages=3 -s ROBOTSTXT_OBEY=False -s CLOSESPIDER_ITEMCOUNT=0

# 【全国全城市覆盖】单进程抓链家所有有站城市（约 145 城）的开放首页，解除条数上限：
#   先确保 cities_all.txt 存在（链家城市目录解析结果，仓库已带；如需重建见“全国城市目录”一节）
scrapy crawl lianjia -a all_cities=1 -s ROBOTSTXT_OBEY=False -s HTTPCACHE_ENABLED=False -s CLOSESPIDER_ITEMCOUNT=0

# 指定多城（逗号分隔，可 子域:中文名）：
scrapy crawl lianjia -a cities=bj,sh:上海,hz,cq -s ROBOTSTXT_OBEY=False -s CLOSESPIDER_ITEMCOUNT=0
```

> **全国城市目录（`cities_all.txt`）**：由链家城市目录页 `https://www.lianjia.com/city/` 解析而来
> （`子域名\t中文名` 每行一条）。如需重建（链家增删城市时）：
> ```bash
> python - <<'PY'
> import urllib.request, re
> ua='Mozilla/5.0 ... Chrome/124.0.0.0 Safari/537.36'
> html=urllib.request.urlopen(urllib.request.Request('https://www.lianjia.com/city/',headers={'User-Agent':ua}),timeout=20).read().decode('utf-8','ignore')
> pairs=re.findall(r'href="https?://([a-z]+)\.lianjia\.com/?"[^>]*>\s*([^<\s][^<]*?)\s*<',html)
> uniq={}; skip={'www','m','news','image','s1','clogin','hip','passport'}
> for s,n in pairs:
>     if s not in skip: uniq.setdefault(s,n.strip())
> open('cities_all.txt','w',encoding='utf-8').write('\n'.join(f'{s}\t{n}' for s,n in sorted(uniq.items())))
> PY
> ```

> **覆盖范围与上限（实测 2026-06-03）**：链家全国共约 **145 个有站城市**，一次 `all_cities=1`
> 实测入库 **4347 条**、覆盖 **139 城 / 2029 区商圈 / 29 个省级行政区**。注意三点客观限制（均**不绕过**）：
> ① **市**：仅链家有站的城市，并非全国所有县市；个别城市首页会临时限流返回空；
> ② **区**：`/ershoufang/{区}/` 需**登录**（302 跳 `clogin.lianjia.com`），无法逐区穷举，区/商圈只能取自每城首页房源；
> ③ **省**：全国 31 个大陆省级单位里**缺 青海、西藏**——链家在该两地无独立站点。

> 实测：`-a city=bj -a max_pages=1 -s ROBOTSTXT_OBEY=False` 可抓取并入库约 30 条北京真实房源。

**Spider 参数**

| 参数 | 含义 | 默认 |
|------|------|------|
| `city` | 链家城市子域名缩写（`bj`/`sh`/`gz`/`sz`/`hz`/`cd`/`jn`/`qd`…） | `bj` |
| `city_name` | 入库用的城市中文名（缺省按 `city` 查表） | 由 `city` 推断 |
| `all_cities` | 抓**全国所有有站城市**（读 `cities_all.txt`，每城仅抓首页） | `0` |
| `cities` | 指定多城，逗号分隔，如 `bj,sh:上海,hz`（每城仅抓首页） | 空 |
| `max_pages` | 最多翻几页列表 | `5` |
| `region` | 城市内板块/区拼音（链家 URL 段），留空抓全市 | 空 |
| `follow_detail` | 是否跟进详情页补充 楼层/经纬度（链家详情页有验证码，默认关闭） | `0` |

**常用 Scrapy 开关**（`-s KEY=VALUE`）：`CLOSESPIDER_ITEMCOUNT`（抓取上限）、`DOWNLOAD_DELAY`（请求间隔）、`LOG_LEVEL`。

## 3. 数据落地

- 管道 `DatabasePipeline` 复用后端 `backend/app.py` 的应用工厂与 `config.py` 的数据库配置，
  因此**写入的就是后端在用的同一个库**（`backend/.env` 的 `DATABASE_URL`，或默认 `backend/housing.db`）。
- 自动 `get_or_create` 城市/行政区（抓到的城市会并入已有同名城市）。
- 以**详情页 URL（`source_url`）去重**，重复运行不会写入重复房源。
- 抓取的房源 `source="lianjia"`，便于与 `seed` 合成数据区分。

跑完后验证（从 `backend/` 目录）：

```bash
cd ../backend
../.venv/bin/python -c "from app import app, db; from models import Property; ctx=app.app_context(); ctx.push(); print('lianjia 房源数:', Property.query.filter_by(source='lianjia').count())"
```

## 4. 同时导出文件（可选）

如还想留一份 CSV/JSON 备份，追加 `-O`（覆盖）或 `-o`（追加）：

```bash
scrapy crawl lianjia -a city=bj -a max_pages=3 -O out/beijing.csv
scrapy crawl lianjia -a city=bj -a max_pages=3 -O out/beijing.json
```

## 5. 常见问题

- **列表页「未解析到房源」/ 返回验证页**：目标站反爬所致。请降低频率、确认有权抓取；
  **不要**用代理轮换/验证码破解去绕过。可先用浏览器确认该城市/板块 URL 是否正常。
- **`ModuleNotFoundError: app/config/models`**：未把 Scrapy 装进项目根 `.venv`，
  或不在 `crawler/` 目录运行。请按 §1 安装、在 `crawler/` 下执行。
- **页面结构变化导致字段为空**：链家改版后选择器可能失效，调整 `spiders/lianjia.py`
  里的 CSS 选择器即可（解析逻辑已做容错，不会整条崩）。
- **写入 MySQL 报字段超长**：管道已按列长度截断；如仍有问题检查数据库字符集为 `utf8mb4`。

## 6. 与项目内旧爬虫骨架的关系

`backend/spider/` 是早期的轻量采集**骨架**（演示用，默认不联网）。本 `crawler/` 是基于
**Scrapy** 的正式采集器，二者独立；推荐使用本目录。

## 7. 可选：用"浏览器登录态"抓更深层页面（区/详情，谨慎）

链家把**区/板块页、第 2 页起、详情页**挡在了**登录/验证码**之后，匿名只能抓每城首页（约 30 条）。
如你愿意用**自己的账号**登录后再抓，可把登录后的 Cookie 提供给爬虫——这是使用你本人登录会话，
**不是绕过登录、也不破解验证码**。

> ⚠️ **风险（务必知悉）**：① 登录态下的自动化抓取**大概率违反链家 ToS**，**可能导致账号被限制/封禁**；
> ② Cookie 等同于你的登录凭证，**切勿提交到仓库或发给任何人**（已在 `.gitignore` 忽略 `cookies.txt`），且会过期；
> ③ 即便登录，仍可能触发验证码——那一步本爬虫**不会**处理。请**低频小量**抓取，风险自负。

**步骤**
1. 浏览器登录 lianjia.com → F12 打开开发者工具 → Network/网络 → 刷新一个 `ershoufang` 页面
   → 点该请求 → 复制请求头里的整段 **`Cookie`** 值。
2. 存到本地（二选一，**不要粘到对话里**）：
   - 文件：把整段 Cookie 写入 `crawler/cookies.txt`（单行）；或
   - 环境变量：`export LIANJIA_COOKIE='整段cookie'`
3. 低频运行（建议加大延迟，减小账号风险）：
   ```bash
   scrapy crawl lianjia -a city=bj -a city_name=北京 -a auto_regions=1 -a max_regions=4 \
     -s ROBOTSTXT_OBEY=False -s DOWNLOAD_DELAY=8
   ```
   配了 Cookie 后，`settings.py` 会自动启用 `CookieHeaderMiddleware` 给每个 lianjia 请求带上登录态。

> 自动板块模式（`-a auto_regions=1`）：先解析城市的区列表，再逐区抓首页，`district` 存为区名
> （如"海淀区"）。`-a max_regions=N` 限制区数量。
