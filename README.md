# 🤖 AI板块投资分析师 Skill

> 基于 TRAE SOLO 打造，每日自动生成 AI 产业链投资报告（PDF），覆盖 14 个细分赛道、18+ 推荐基金、择时信号与操作建议。

---

## 📸 效果预览

[在此处粘贴 PDF 截图或 GIF 演示]

---

## 🎯 解决的问题

AI 板块投资有三大痛点：

| 痛点 | 本 Skill 的解法 |
|------|----------------|
| 赛道太多，不知道怎么分类 | 14 个细分赛道，按上游/中游/下游三层分组 |
| 每天看盘太累，信息散落各处 | 一键生成 PDF 报告，8 个模块覆盖估值/资金/资讯/建议 |
| 不知道该买 ETF 还是主动型基金 | 内置 18 只推荐基金，按板块区分 ETF 和主动型 |

---

## ✨ 核心亮点

- **产业链全覆盖**：上游算力（6赛道）→ 中游模型（2赛道）→ 下游应用（6赛道）
- **数据驱动模板**：HTML 完全由 JSON 驱动，赛道/基金增删无需改代码
- **择时信号系统**：PE 分位 + 恐惧贪婪指数 + MACD 三位一体判断
- **ETF vs 主动型智能推荐**：上游标的集中→推 ETF；下游标的分散→推主动型
- **自动增量更新**：每次运行搜索最新基金上市/清盘信息，更新知识基线
- **首选 Playwright 渲染**：效果最佳，支持完整 CSS 样式（渐变仪表盘、emoji）；无法使用时降级 WeasyPrint

---

## 📂 文件结构

```
ai-sector-investor-skill/
├── SKILL.md                              # Skill 定义（触发/流程/规则）
├── README.md                             # 本文件
├── references/                           # 知识基线（独立维护）
│   ├── market-baseline.md                # AI产业链基线、赛道与基金映射
│   └── investment-rules.md               # 择时信号规则、季度轮动配置
├── scripts/                              # 执行脚本
│   ├── render_pdf.py                     # Playwright 首选（效果最佳）
│   └── render_pdf_simple.py              # WeasyPrint 兜底（无需浏览器）
└── templates/
    ├── ai-sector-briefing-playwright.html  # 完整效果版（conic-gradient、emoji）
    └── ai-sector-briefing-weasyprint.html  # 兼容降级版（纯色、CSS 圆点）
```

---

## 🚀 使用方式

### 前置要求

**首选 — Playwright**（效果最佳，支持渐变仪表盘等高级效果）：

```bash
# 1. 安装 Python 包
pip install playwright --break-system-packages

# 2. 安装浏览器
python -m playwright install chromium

# 3. 安装系统依赖（Playwright 自动检测环境并安装正确版本）
python -m playwright install-deps chromium

# 4. 渲染
python scripts/render_pdf.py templates/ai-sector-briefing-playwright.html output/AI板块投资报告.pdf
```

**降级 — WeasyPrint**（Playwright 无法使用时，纯 Python 无需浏览器）：
```bash
pip install weasyprint --break-system-packages
# 传入 Step 2 生成的动态 HTML，脚本自动提取 DATA 并使用 WeasyPrint 模板渲染
python scripts/render_pdf_simple.py <动态HTML路径> output/AI板块投资报告.pdf
```

> **注意**：
> - Playwright 需要系统级依赖库（如 libatk、libxcomposite 等），首次运行前需安装
> - 两个脚本都接收 Step 2 生成的同一个动态 HTML 文件，不需要手动切换模板
> - `render_pdf_simple.py` 会自动查找 `ai-sector-briefing-weasyprint.html` 模板

### 在 TRAE SOLO 中使用

1. 将 `ai-sector-investor-skill` 文件夹放入 SOLO 的 skills 目录
2. 在对话中输入：「生成今天的 AI 板块投资报告」
3. SOLO 自动执行：搜索数据 → 更新赛道/基金 → 生成 HTML → 渲染 PDF
4. 在工作目录找到 `AI板块投资报告.pdf`

### 作为定时任务

配合 SOLO 的 Schedule 工具，可设置每日早 8:30 / 晚 15:30 自动生成推送。

---

## 📄 PDF 报告结构

```
┌─────────────────────────────────────┐
│  🤖 AI板块投资报告                    │
│  YYYY年MM月DD日  综合信号             │
├─────────────────────────────────────┤
│  一、估值温度计                       │
│  二、恐惧贪婪指数                     │
│  三、AI产业链全景（14个细分赛道）      │
│  四、资金流向                         │
│  五、择时信号面板                     │
│  六、推荐基金（ETF+主动型）           │
│  七、AI产业重要资讯                   │
│  八、今日操作建议                     │
│  免责声明                             │
└─────────────────────────────────────┘
```

---

## 🔧 技术架构

```
数据获取(WebSearch×3)
     ↓
增量更新基线(Step 1.5)
     ↓
组装 JSON 数据
     ↓
注入 HTML 模板(DATA 对象)
     ↓
首选 Playwright → PDF（降级 WeasyPrint）
```

---

## ⚠️ 免责声明

本 Skill 生成的报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。
