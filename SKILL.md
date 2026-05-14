---
name: ai-sector-investor
version: 1.0.0
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

以下搜索每次运行时根据当前年月动态替换时间。共 3 次搜索：

1. **市场数据**：`"{当前年月} AI板块 人工智能 半导体 机器人 算力 涨跌幅 PE估值 北向资金"`
2. **产业资讯**：`"{当前年月} AI人工智能 最新新闻 政策 半导体 机器人 大模型"`
3. **基金与赛道更新**：`"{当前年月} AI 人工智能 半导体 机器人 ETF 新上市 清盘 新概念"`

### Step 1.5：增量更新知识基线

将 Step 1 的三次搜索结果与 `references/market-baseline.md` 中的基线对比，分两步操作：

#### 1.5a 结构更新（用第 3 次搜索的结果）

| 更新项 | 对比来源 | 操作 |
|--------|---------|------|
| **sectors 赛道** | 第 3 次搜索中出现的 AI 新概念/新赛道 | 基线中不存在 → 追加；基线中存在 → 保留 |
| **funds 基金** | 第 3 次搜索中出现的 ETF 新上市/清盘 | 新上市且基线中不存在 → 追加；清盘/退市 → 从基线中移除 |

#### 1.5b 数值更新（用第 1 次搜索的结果）

| 更新项 | 对比来源 | 操作 |
|--------|---------|------|
| **sectors 的 change / pe_pct** | 从第 1 次搜索的市场数据提取 | 逐赛道填入最新数值 |
| **indices 的 pe_pct** | 从第 1 次搜索的指数估值数据提取 | 填入 4 个指数的 PE 百分位 |
| **flow 的资金数据** | 从第 1 次搜索的北向/主力资金数据提取 | 填入 north_1d/5d/20d 和 main_1d |
| **fear_greed** | 从第 1 次搜索提取或自行计算 | 填入 value 和 zone |
| **funds 代表公司** | 从第 1 次搜索的各赛道龙头新闻推断 | 每赛道保留前 3 名 |

> 基线位于 `references/market-baseline.md`。每次运行时**必须先验证再使用**，不能直接拿来生成报告。

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
    {"name": "中韩半导体ETF", "code": "159352/513310", "type": "ETF", "layer": "up"},
    {"name": "永赢科技智选混合C", "code": "022365", "type": "主动型", "layer": "mid"}
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

**首选 — Playwright**（效果最佳，支持渐变仪表盘等高级效果）：
```bash
# 首次需安装依赖
pip install playwright --break-system-packages
python -m playwright install chromium
python -m playwright install-deps chromium

# 渲染
python scripts/render_pdf.py templates/ai-sector-briefing-playwright.html output/AI板块投资报告.pdf
```

**降级 — WeasyPrint**（Playwright 无法使用时降级，纯 Python 无需浏览器）：
```bash
pip install weasyprint --break-system-packages
python scripts/render_pdf_simple.py templates/ai-sector-briefing-playwright.html output/AI板块投资报告.pdf
```

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

- `references/market-baseline.md` - AI产业链基线、赛道与基金映射
- `references/investment-rules.md` - 择时信号规则、季度轮动配置

## 输出规范

- 最终输出：PDF格式投资报告
- 语言：中文
- 必须包含：数据来源标注 + 免责声明
