# 宴江南 AI 老板经营诊断系统

面向青岛城阳宴江南（汇海路店）的演示型 MVP。V2 从「AI 客户经营工具」升级为「AI 老板经营诊断系统」：每天帮老板发现经营问题，并告诉下一步该做什么。

本版本使用模拟数据，不接入真实收银、会员或桌台系统。翻台与菜品成本均为演示数据。

## 功能

- AI 经营驾驶舱、AI 经营机会中心、AI 老板日报
- 菜品经营分析（四象限）、AI 菜单诊断
- 营业异常分析、翻台效率分析
- AI 员工推荐菜
- 客户管理、AI 客户召回、宴请客户
- AI 营销助手、AI 评价分析

## 技术栈

- 前端：React 18、TypeScript、Vite、Ant Design、ECharts
- 后端：Python、FastAPI、SQLAlchemy
- 数据库：PostgreSQL
- AI：阿里云百炼兼容模式（qwen-plus）

## 启动

登录账号：`admin` / `admin123`

开着 VPN 时请访问 **http://127.0.0.1:5173**。

### 1. 后端

```bash
cd backend
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

首次启动会建表并导入 `data/demo/` 模拟数据。

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

- 前端：http://127.0.0.1:5173
- 后端：http://127.0.0.1:8000
- API 文档：http://127.0.0.1:8000/docs

## 环境变量

`.env` 示例见 `.env.example`。本地 PostgreSQL：

```text
DATABASE_URL=postgresql+psycopg://postgres:root@127.0.0.1:5432/yanjiangnan_ai
OPENAI_API_KEY=your_dashscope_api_key
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-plus
LLM_DEFAULT_TEMPERATURE=0.1
DEMO_MODE=false
```

## Demo 模式

`DEMO_MODE=true` 或未配置 Key 时，AI 使用预设结果，无网络也能完整演示。接口失败时页面不会崩溃。

## 演示流程（5～8 分钟）

1. 打开 AI 经营机会中心，看「今日最值得做」和 5～8 条机会。
2. 点开晚餐高峰效率，看 96 分钟 vs 72 分钟的数据证据。
3. 筛选菜品机会，看烤腱子肉和潜力菜。
4. 看高价值客户召回、周末上菜慢评价、高预算宴请。
5. 回到驾驶舱，确认 Top 3 机会；需要时再打开翻台、菜单、召回详情。
