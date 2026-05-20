---
name: ai-sector-investor
version: 1.2.0
description: "AI板块投资分析与PDF报告生成。当用户需要分析AI板块投资、查看板块轮动、获取基金推荐、生成投资报告时使用。最终输出为PDF格式。"
---

# AI板块投资分析师

为用户提供AI板块（人工智能产业链）的投资分析服务，最终生成**PDF格式的投资报告**。

## 触发场景

- 用户提到"AI板块"、"人工智能投资"、"半导体基金"、"机器人ETF"等关键词
- 用户需要分析AI产业链上下游轮动
- 用户需要高位止盈/低位建仓的择时建议
- 用户要求生成投资报告、播报、分析

## 执行流程（固定输出PDF）

### Step 1：数据获取（WebSearch）

以下搜索每次运行时根据当前年月动态替换时间。共 **4 次搜索**：

1. **市场数据**：`"{当前年月} AI板块 人工智能 半导体 机器人 算力 涨跌幅 PE估值 北向资金"`
2. **产业资讯**：`"{当前年月} AI人工智能 最新新闻 政策 半导体 机器人 大模型"`
3. **基金业绩排名**：`"{当前年月} AI人工智能基金 业绩排名 近一年收益率 site:fund.eastmoney.com OR site:finance.sina.com.cn"`
4. **赛道新概念**：`"{当前年月} AI 人工智能 半导体 机器人 ETF 新上市 清盘 新概念"`

> **搜索来源限制**：优先使用权威金融网站
> - `site:fund.eastmoney.com` - 天天基金网
> - `site:finance.eastmoney.com` - 东方财富
> - `site:finance.sina.com.cn` - 新浪财经
> - `site:cs.com.cn` - 中国证券报
> - `site:cnstock.com` - 上海证券报

### Step 1.5：基金动态发现与分层

**纯动态搜索，不依赖固定基线**。从 Step 1 第 3 次搜索（基金业绩排名）提取当日表现最佳的 AI 主题基金，按产业链层级自动分类。

#### 1.5a 基金发现（用第 3 次搜索的结果）

| 操作 | 说明 |
|------|------|
| **提取基金** | 从搜索结果提取基金名称、代码、近一年收益率 |
| **去重排序** | 按收益率排序，同名基金保留业绩最优者 |
| **失败处理** | 搜索失败或无结果时，该层级显示"暂无推荐" |

#### 1.5b 基金分层映射

根据基金名称/投资方向关键词自动分类：

| 层级 | 关键词 | 示例 |
|------|--------|------|
| **上游** | 半导体、芯片、算力、光模块、存储、服务器、GPU | 芯片ETF、半导体基金 |
| **中游** | 大模型、平台、云计算、软件、MaaS、开发 | AI平台基金、云计算ETF |
| **下游** | 应用、机器人、智能驾驶、AI+、传媒、医疗、金融 | 机器人ETF、AI应用基金 |

> **分类规则**：匹配关键词即归入对应层级；同时匹配多个层级时，按上游>中游>下游优先级；未匹配默认归入下游。

#### 1.5c 数值更新（用第 1 次搜索的结果）

| 更新项 | 对比来源 | 操作 |
|--------|---------|------|
| **sectors 的 change / pe_pct** | 从第 1 次搜索的市场数据提取 | 逐赛道填入最新数值 |
| **indices 的 pe_pct** | 从第 1 次搜索的指数估值数据提取 | 填入 4 个指数的 PE 百分位 |
| **flow 的资金数据** | 从第 1 次搜索的北向/主力资金数据提取 | 填入 north_1d/5d/20d 和 main_1d |
| **fear_greed** | 从第 1 次搜索提取或自行计算 | 填入 value 和 zone |
| **funds 业绩** | 从第 3 次搜索提取 | 填入 return_1y（近一年收益率%） |

> **数据来源**：Step 1 搜索结果 + Step 1.5 动态发现

#### 1.5d 持仓验证

对 Top 基金（每层级前2名）二次搜索持仓，确认分层准确性：
- 搜索词示例：`"{基金名称} 持仓 重仓股 2026年"`
- 如果实际持仓与名称关键词分层矛盾，调整到正确层级
- 如果搜索失败，保持按名称关键词分层

### Step 2：生成HTML报告

使用 `templates/ai-sector-briefing-playwright.html` 模板（**首选方案**）。该模板为**纯数据驱动**：将下方 JSON 注入模板顶部的 `DATA` 对象，打开即可渲染。无需修改 HTML 结构。

> **两套模板说明**：
> - `ai-sector-briefing-playwright.html` - 完整效果版，支持 `conic-gradient` 渐变仪表盘、动态渲染
> - `ai-sector-briefing-weasyprint.html` - 兼容降级版，纯色替代渐变，纯静态 HTML 无需 JavaScript

```json
{
  "date": "YYYY年MM月DD日 周X",
  "signal_level": "warn",
  "signal_text": "🟡 中性偏谨慎",
  "indices": [
    {"name": "沪深300", "pe_pct": 62},
    {"name": "中证500", "pe_pct": 48},
    {"name": "科创50", "pe_pct": 95},
    {"name": "创业板指", "pe_pct": 55}
  ],
  "fear_greed": {"value": 62, "zone": "偏贪婪"},
  "flow": {"north_1d": 12.5, "north_5d": 38.2, "north_20d": 156.8, "main_1d": -8.3},
  "sectors": [
    {"name": "AI训练芯片", "layer": "up", "change": 2.1, "pe_pct": 88},
    {"name": "推理芯片/ASIC", "layer": "up", "change": 3.5, "pe_pct": 72}
  ],
  "funds": [
    {"name": "广发远见智选混合A", "code": "016873", "type": "主动型", "layer": "up", "return_1y": 111.2},
    {"name": "富国创新科技混合A", "code": "002692", "type": "主动型", "layer": "mid", "return_1y": 247.3}
  ],
  "news": [
    {"text": "新闻内容", "impact": "利好/利空/中性"}
  ],
  "advice_title": "核心：上游分批止盈，下游逢低布局",
  "advice": "🔹 <b>AI芯片ETF</b>：PE分位88%，止盈30-50%<br>🔹 <b>机器人ETF</b>：PE分位45%，逐步布局",
  "footer_text": "数据来源：公开市场信息 · YYYY.MM.DD"
}
```

**字段说明**：
| 字段 | 类型 | 说明 |
|------|------|------|
| `sectors[].change` | number | 昨日涨跌幅(%)，从 Step 1 第 1 次搜索提取 |
| `sectors[].pe_pct` | number | PE 近 5 年百分位(0-100) |
| `sectors[].layer` | string | 产业链层级：`up`/`mid`/`down` |
| `flow.north_1d` | number | 北向资金近 1 日净买入（亿元） |
| `flow.main_1d` | number | 主力资金近 1 日净买入（亿元） |
| `fear_greed.value` | number | 恐惧贪婪指数数值(0-100) |
| `news[].impact` | string | 对板块影响：`利好`/`利空`/`中性` |

**数据填充规则**：
- 所有数值从 Step 1 WebSearch + Step 1.5 验证后的数据提取
- `signal_level`：warn/danger/safe，根据 `references/investment-rules.md` 中的择时规则推算
- `sectors` 和 `funds` 的 `layer` 取值为 `up`/`mid`/`down`，模板自动按层分组渲染
- `fear_greed.zone`：0-25极度恐惧 / 25-50中性 / 50-75偏贪婪 / 75-100极度贪婪
- `funds` 中每只基金的操作建议由模板根据其所在 layer 的平均 PE 分位自动计算

### Step 3：HTML渲染为PDF

**核心原则**：
1. **不要自己生成 static HTML**，必须使用 skill 目录下的模板
2. 优先 Playwright，失败时降级 WeasyPrint
3. WeasyPrint 降级时，`render_pdf_simple.py` 会自动从 Step 2 的动态 HTML 中提取 DATA，并使用 `ai-sector-briefing-weasyprint.html` 模板渲染

**首选 — Playwright**（效果最佳，支持渐变仪表盘等高级效果）：

```bash
# 1. 安装 Python 包
pip install playwright --break-system-packages

# 2. 安装浏览器
python -m playwright install chromium

# 3. 安装系统依赖（Playwright 自动检测环境并安装正确版本）
python -m playwright install-deps chromium

# 4. 渲染（使用 Step 2 生成的动态 HTML）
python scripts/render_pdf.py <Step2生成的动态HTML路径> output/AI板块投资报告.pdf
```

**降级 — WeasyPrint**（Playwright 无法使用时降级，纯 Python 无需浏览器）：

```bash
pip install weasyprint --break-system-packages

# 直接传入 Step 2 生成的动态 HTML，脚本会自动：
# 1. 从 HTML 中提取 const DATA = {...}
# 2. 自动查找 ai-sector-briefing-weasyprint.html 模板
# 3. 渲染模板并生成 PDF
python scripts/render_pdf_simple.py <Step2生成的动态HTML路径> output/AI板块投资报告.pdf
```

> **模板说明**：
> - `ai-sector-briefing-playwright.html` — Playwright 专用，数据通过 `const DATA = {...}` 注入，JavaScript 动态渲染
> - `ai-sector-briefing-weasyprint.html` — WeasyPrint 专用，使用 `{{placeholder}}` 语法，`render_pdf_simple.py` 会自动处理
> - **两个脚本都接收 Step 2 生成的同一个动态 HTML 文件**，不需要手动切换模板

### Step 4：验证交付

PDF 生成后**必须验证**，不能直接交付：

1. **检查文件大小**：`ls -la output.pdf`，正常报告应 > 100KB，< 10KB 说明渲染失败
2. **失败处理**：如果文件异常小，说明 HTML 数据注入或模板渲染有问题，需排查：
   - 检查 HTML 中 `const DATA` 是否正确替换
   - WeasyPrint 方案检查模板渲染日志是否有未替换的 `{{}}` 标记
   - 必要时重新执行 Step 2 和 Step 3
3. **交付**：验证通过后提供 PDF 文件链接

## 报告结构（PDF固定格式）

```
┌─────────────────────────────────────┐
│  🤖 AI板块投资报告                    │
│  YYYY年MM月DD日  综合信号             │
├─────────────────────────────────────┤
│  一、估值温度计（indices数据）         │
│  二、恐惧贪婪指数                     │
│  三、AI产业链全景（sectors数据）      │
│  四、资金流向                         │
│  五、择时信号面板                     │
│  六、推荐基金（funds数据）            │
│  七、AI产业重要资讯（news数据）       │
│  八、今日操作建议                     │
│  免责声明                             │
└─────────────────────────────────────┘
```

## 参考文档

- `references/investment-rules.md` - 择时信号规则、季度轮动配置

## 输出规范

- 最终输出：PDF格式投资报告
- 语言：中文
- 必须包含：数据来源标注 + 免责声明
