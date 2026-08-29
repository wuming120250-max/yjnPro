# 宴江南 AI 门店经营助手

面向青岛城阳宴江南（汇海路店）的演示型 MVP：在现有经营数据之上增加 AI 分析层，帮助老板发现该召回的客户、生成营销动作，并跟进高价值宴请线索。

本版本使用模拟数据，不接入真实收银、会员或点评平台。本机直接用 Python + Node 启动，连接本机 PostgreSQL。

## 功能

- AI 经营驾驶舱
- 客户管理
- AI 客户召回（高价值沉睡客户 + 微信话术）
- AI 营销助手
- AI 评价分析
- 宴请客户线索管理

## 启动

登录账号、数据库密码和 AI 密钥都写在本地 `.env` 里（从 `.env.example` 复制后自行填写），不要提交到 GitHub。

默认已接入阿里云百炼（通义千问），`DEMO_MODE=false`。演示时会真实调用 `qwen-plus`。若接口失败，页面不会崩溃，会回退到预设结果。

开着 VPN 时请访问 **http://127.0.0.1:5173**，不要用 `localhost`（代理可能把 localhost 劫持到虚拟网段，页面会空白）。

### 1. 后端

不要使用系统全局 Python。

```bash
cd backend
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

首次启动会自动建表并导入 `data/demo/` 模拟数据。

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

访问：

- 前端：http://127.0.0.1:5173
- 后端：http://127.0.0.1:8000
- API 文档：http://127.0.0.1:8000/docs

## 配置

```bash
copy .env.example .env
```

在 `.env` 中填写数据库连接、百炼 API Key、JWT 密钥和后台登录密码。完整字段说明见 `.env.example`。

密钥只放在 `.env` 中，不要写进代码或提交到 GitHub。现场若不想走真实接口，把 `DEMO_MODE` 改成 `true`。

## 模拟数据

数据文件在 `data/demo/`：

- 客户不少于 200 条
- 订单不少于 1000 条
- 评价不少于 100 条
- 宴请线索不少于 30 条

重新生成 CSV：

```bash
python backend/scripts/generate_demo_data.py
```

重新导入数据库：

```bash
cd backend
python -m scripts.init_db
```

## 演示路径

1. 打开 AI 经营驾驶舱，看今日数据和 AI 今日发现。
2. 进入 AI 客户召回，查看高价值沉睡客户，打开「赵女士」做 AI 分析并生成微信话术。
3. 进入 AI 评价分析，点击「AI分析全部评价」。
4. 进入 AI 营销助手，用「家庭聚餐 / 特色海鲜 / 满388赠特色菜」生成方案。
5. 进入宴请客户，查看「张先生」25 人公司聚餐线索并做 AI 分析。
