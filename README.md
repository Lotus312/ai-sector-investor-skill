# AI板块投资分析师 Skill

> 基于 TRAE SOLO 打造，每日自动生成 AI 产业链投资报告（PDF），覆盖 14+ 细分赛道、动态发现基金、择时信号与操作建议。

---

## 效果预览

[在此处粘贴 PDF 截图或 GIF 演示]

---

## 解决的问题

AI 板块投资有三大痛点：

| 痛点 | 本 Skill 的解法 |
|------|----------------|
| 赛道太多，不知道怎么分类 | 14+ 细分赛道，按上游/中游/下游三层分组 |
| 每天看盘太累，信息散落各处 | 一键生成 PDF 报告，8 个模块覆盖估值/资金/资讯/建议 |
| 不知道该买 ETF 还是主动型基金 | 动态发现基金，按板块区分 ETF 和主动型，新基金标 `[新上]` |

---

## 核心亮点

- **纯动态基金发现**：不依赖固定基线，每次运行从搜索结果实时提取，按关键词自动分层
- **持仓验证 + 业绩排序**：Top 基金二次搜索持仓确认分层，同层级按近一年收益率排序
- **产业链全覆盖**：上游算力（6赛道）→ 中游模型（2赛道）→ 下游应用（6+赛道）
- **数据驱动模板**：HTML 完全由 JSON 驱动，赛道/基金增删无需改代码
- **择时信号系统**：PE 分位 + 恐惧贪婪指数 + 资金流向三位一体判断
- **ETF vs 主动型智能推荐**：上游标的集中→推 ETF；下游标的分散→推主动型
- **首选 Playwright 渲染**：效果最佳；无法使用时降级 WeasyPrint，两个模板输出一致

---

## 文件结构

```
ai-sector-investor-skill/
├── SKILL.md                              # Skill 定义（触发/流程/规则）
├── README.md                             # 本文件
├── CHANGELOG.md                          # 版本更新日志
├── references/
│   └── investment-rules.md               # 择时信号规则、季度轮动配置
├── scripts/
│   ├── render_pdf.py                     # Playwright 首选（效果最佳）
│   └── render_pdf_simple.py              # WeasyPrint 兜底（无需浏览器）
└── templates/
    ├── ai-sector-briefing-playwright.html  # 完整效果版（纯色仪表盘）
    └── ai-sector-briefing-weasyprint.html  # 兼容降级版（纯静态 HTML）
```

---

## 使用方式

### 前置要求

**首选 — Playwright**（效果最佳）：

```bash
pip install playwright --break-system-packages
python -m playwright install chromium
python -m playwright install-deps chromium
```

**降级 — WeasyPrint**（纯 Python 无需浏览器）：
```bash
pip install weasyprint --break-system-packages
```

> 两个脚本都接收 Step 2 生成的同一个动态 HTML 文件，不需要手动切换模板。

### 在 TRAE SOLO 中使用

1. 将 `ai-sector-investor-skill` 文件夹放入 SOLO 的 skills 目录
2. 在对话中输入：「生成今天的 AI 板块投资报告」
3. SOLO 自动执行：4 次搜索 → 动态发现基金 → 持仓验证 → 生成 HTML → 渲染 PDF
4. 在工作目录找到 `AI板块投资报告.pdf`

### 作为定时任务

配合 SOLO 的 Schedule 工具，可设置每日 18:00 盘后自动生成推送。

---

## PDF 报告结构

```
┌─────────────────────────────────────┐
│  AI板块投资报告                      │
│  YYYY年MM月DD日  综合信号             │
├─────────────────────────────────────┤
│  一、估值温度计                       │
│  二、恐惧贪婪指数                     │
│  三、AI产业链全景（14+细分赛道）      │
│  四、资金流向                         │
│  五、择时信号面板                     │
│  六、推荐基金（ETF+主动型）           │
│  七、AI产业重要资讯                   │
│  八、今日操作建议                     │
│  免责声明                             │
└─────────────────────────────────────┘
```

---

## 技术架构

```
数据获取(WebSearch x4)
     ↓
基金动态发现与分层(Step 1.5)
  → 按关键词分层（上游/中游/下游）
  → Top基金持仓验证
  → 同层级按业绩排序
     ↓
组装 JSON 数据
     ↓
注入 HTML 模板(DATA 对象)
     ↓
首选 Playwright → PDF（降级 WeasyPrint）
```

---

## 免责声明

本 Skill 生成的报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。
