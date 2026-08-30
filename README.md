# 🏆 七猫榜单风向标 · Qimao Rank Tracker

> 📚 覆盖**七猫免费小说男生 + 女生频道榜单**（新书榜 / 大热榜 / 完结榜 / 收藏榜），每日自动追踪热度数据并结合 AI 生成趋势分析，部署为在线看板。

---

## ✨ 功能概览

| 功能 | 说明 |
|------|------|
| 🕷️ 自动爬取 | 每日定时抓取七猫男生/女生频道共 8 个榜单的 Top 20（纯静态页面解析，无需无头浏览器） |
| 📊 趋势对比 | 自动对比相邻两天数据：新上榜 / 掉榜 / 排名变化 / 热度增长 |
| 🤖 AI 风向分析 | 接入 OpenAI 兼容 API，按榜单生成市场趋势速评 |
| 🧭 榜单风向标 | 独立趋势页聚合多日数据，总结男生/女生榜单热点和高频题材；未配置 API 时自动规则兜底 |
| 🖥️ 精美看板 | 暗色编辑风格仪表盘，带打字机动画和瀑布流书籍卡片 |
| 📱 移动适配 | 完整的移动端适配，侧边栏抽屉式菜单 |
| 🔌 数据接口 | 生成静态 `lastest` JSON 接口，可按榜单读取最新数据 |
| ⚡ 全自动化 | GitHub Actions + GitHub Pages，零服务器运维 |

---

## 🚀 食用指南

### 前置条件

- **Python 3.9+**
- **Git**
- 一个 GitHub 账号
- （可选）一个 OpenAI 兼容 API 的密钥，用于 AI 分析

### 第一步：Fork / 使用本仓库

### 第二步：开启 GitHub Pages

1. 进入仓库 → **Settings** → **Pages**
2. Source 选择 **GitHub Actions**
3. 保存即可，后续由工作流自动部署

### 第三步：配置 Secrets（可选，开启 AI 分析）

进入仓库 → **Settings** → **Secrets and variables** → **Actions**，添加：

| Secret 名称 | 说明 | 示例 |
|---|---|---|
| `API_BASE_URL` | OpenAI 兼容 API 的地址 | `https://api.openai.com/v1` |
| `API_KEY` | API 密钥 | `sk-xxxxxxxxxxxxx` |
| `API_MODEL` | 模型名称 | `gpt-4o-mini` |

> **💡 提示：** 不配置这三个 Secret 时，系统将自动使用基于规则的摘要替代 AI 分析，**不影响核心功能**。

### 第四步：手动触发首次运行

1. 进入仓库 → **Actions** → 选择 **Daily Qimao Rank Scraper**
2. 首次进入如提示启用 Workflows，点击确认启用
3. 点击 **Run workflow** → **Run**

运行成功后，看板即上线：`https://<你的用户名>.github.io/QimaoRankTracker/`

之后每天北京时间早上 8:47 自动抓取。

### 本地运行

```bash
# 1. 克隆仓库
git clone https://github.com/<你的用户名>/QimaoRankTracker.git
cd QimaoRankTracker

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行爬虫（8 个榜单各抓 Top 20，约 15 秒）
python scrape_qimao_ranks.py

# 5. 构建看板数据（可选，带 AI 分析需设置环境变量）
pip install openai
export API_BASE_URL="https://your-api-endpoint/v1"
export API_KEY="your-api-key"
export API_MODEL="your-model-name"
python scripts/build_qimao.py

# 6. 本地预览前端
python -m http.server 8000
# 打开 http://localhost:8000
```

---

## 📁 项目结构

```
QimaoRankTracker/
├── .github/workflows/
│   └── scrape.yml              # GitHub Actions 自动化工作流
├── css/
│   └── style.css               # 暗色编辑风格主题样式
├── js/
│   ├── app.js                  # 前端渲染逻辑（瀑布流 + 打字机动画）
│   ├── trend.js                # 趋势页逻辑
│   └── book.js                 # 作品详情页逻辑
├── scripts/
│   └── build_qimao.py          # 趋势对比 + AI 分析构建脚本
├── data/
│   ├── qimao_ranks_YYYYMMDD.json  # 每日原始快照
│   ├── latest_ranks.json       # 最新聚合数据（看板数据源）
│   ├── market_summary.json     # 全站热点 AI/规则总结
│   └── trends/
│       └── YYYY-MM-DD.json     # 趋势归档
├── api/
│   └── lastest/                # 最新数据静态接口（all + 按榜单拆分）
├── index.html                  # 仪表盘入口页
├── trend.html                  # 榜单风向标趋势分析页
├── book.html                   # 作品详情页
├── scrape_qimao_ranks.py       # 七猫榜单爬虫（requests + BeautifulSoup）
├── requirements.txt            # Python 依赖
└── README.md                   # 本文件
```

---

## 📊 榜单说明

抓取页面：`https://www.qimao.com/paihang/{boy|girl}/{new|hot|over|collect}/date/`

| 榜单 | 官方规则 |
|------|---------|
| 新书榜 | 总字数低于 50 万、每日更新的七猫原创作品，按昨日热度排行 |
| 大热榜 | 全站高热度作品排行 |
| 完结榜 | 已完结作品排行 |
| 收藏榜 | 按收藏数排行 |

> 数据来源于七猫公开榜单页面，仅用于学习与市场研究，请勿商用。

## 🙏 致谢

项目架构与看板设计基于 [FanqieRankTracker](https://github.com/wen1701/FanqieRankTracker)（番茄小说风向标）改造而来。
