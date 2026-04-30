---
name: ai-daily-research
description: >
  牛马加速器 — 科研牛马的AI科研助手。自动采集、分析并生成每日 AI 新闻日报 + 论文深度研究。
  覆盖国内外新闻 + 6大学术来源(arXiv/OpenAlex/DBLP/CrossRef/OpenReview/Google Scholar) + 11个顶级技术博客。
  支持 PDF 全文提取、作者单位分析、创新点深度解析、外部文章收录(渐进式披露)。
  集成 Karpathy LLM Wiki：论文自动写入个人知识库，概念自动累积，实体自动追踪时间线。
  大厂论文优先。工作日推送到飞书。
version: 1.5.0
author: CODE-BULIAO
license: MIT
tags: [AI, News, Papers, Daily, Research, ArXiv, OpenAlex, LLM]
github: https://github.com/CODE-BULIAO/ai-daily-research
---

# AI Daily Research

自动采集、分析并生成每日 AI 新闻日报 + 论文深度研究的 Hermes Agent Skill。

## 架构

```
脚本采集 (Python) → JSON → LLM总结 → 飞书推送 + Wiki 写入
                                       ↓
                                   ~/wiki/ (个人知识库)
```

**关键设计**：脚本负责数据采集+预处理，LLM负责智能总结+格式化+Wiki写入。分离关注点。

## 数据源

| 类型 | 来源 | 备注 |
|------|------|------|
| 🇨🇳 中文 | 雷峰网/量子位/极客公园/钛媒体/IT之家/36氪 | 36氪限速 |
| 🌍 英文 | Google News(重试机制)/HN(points>30) | |
| ✍️ 博客 | 11个Karpathy推荐顶级技术博客(Simon Willison/GWERN/Paul Graham等) | RSS |
| 📄 学术 | arXiv(PDF全文)+OpenAlex(作者单位)+DBLP(会议) | |
| 📚 出版 | CrossRef(DOI解析,覆盖非arXiv期刊/会议) | 覆盖最广 |
| 📝 顶会 | OpenReview(NeurIPS/ICLR/ICML poster+oral) | 有完整摘要 |

## 大厂论文优先

脚本标记 is_focus_company，论文排序时大厂优先。

**国际**: OpenAI, Google DeepMind, Anthropic, Meta AI, Microsoft, Apple, Amazon, NVIDIA, xAI, Mistral
**国内**: 百度, 阿里, 腾讯, 字节, 华为, 美团, 小米, 商汤, Kimi, 智谱AI, DeepSeek, MiniMax, 蚂蚁

## 增强技术（借鉴 hermes-arxiv-agent）

### PDF 机构提取增强
从 PDF 前2页提取作者单位，包含：
- **ORG_KEYWORDS**: 100+ 机构关键词（Google DeepMind, MIT, 清华, 北大等）
- **CamelCase 分词**: `DepartmentofCS` → `Department of CS`
- **跨行连字符合并**: `Repub-` + `licof Korea` → `Republic of Korea`
- **噪音过滤**: URL、邮件、公式、正文片段
- **启发式判断**: `looks_like_affiliation()` 智能判断是否为真实机构信息

### Excel 持久化记录
- `papers_record.xlsx` 存储所有已处理论文
- 支持 upsert（按 arxiv_id 更新，不重复插入）
- 质量排序：优先保留摘要+单位+日期更完整的记录

### Pending 队列（安全重试）
- `pending_llm_ids.txt` 跟踪 LLM 未完成的论文
- 脚本输出 `[LLM_SUMMARIZATION_REQUIRED]` 标记
- 支持中断后安全恢复

## 输出格式

- 📰 AI 要闻 6条（精选，不分国内外）
- 📄 论文 2篇（大厂优先，含全部作者单位 + 创新点深度解析5维度）
- 📊 趋势 1句话

## 论文去重机制

为避免重复分析同一篇论文，使用 JSON 文件记录已处理的论文：

### 记录文件位置
`/opt/data/cron/output/analyzed_papers.json`

### 文件格式
```json
{
  "last_updated": "2026-04-30",
  "papers": [
    {
      "arxiv_id": "2604.26649",
      "title": "When to Retrieve During Reasoning",
      "date": "2026-04-30",
      "source": "arXiv"
    }
  ]
}
```

### 去重流程
1. **读取记录**：执行前先读取 `analyzed_papers.json`
2. **过滤**：从候选论文中排除已有 arxiv_id 的论文
3. **分析**：只分析未出现过的新论文
4. **写入**：分析完成后，将新论文追加到记录文件
5. **清理**：保留最近 30 天的记录，删除更早的条目

### 去重实现指令
```
在生成日报前，先执行以下检查：
1. 读取 /opt/data/cron/output/analyzed_papers.json（如果存在）
2. 获取已分析的 arxiv_id 列表
3. 从 papers 中排除这些 ID
4. 只从未分析过的论文中选择 2 篇
5. 分析完成后，将新论文 ID 追加到记录文件
```

## 安装依赖

```bash
pip install --break-system-packages pymupdf lark-oapi websockets
```

## 飞书配置

### 前提条件
1. 在飞书开放平台创建应用，获取 App ID 和 App Secret
2. 启用**机器人**能力

### 配置步骤

**1. 设置环境变量**（编辑 Hermes 环境变量文件）
```bash
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket
```

**2. 重启 Gateway**
```bash
hermes gateway restart
```

**3. 设置推送频道**
- 在飞书群里 @机器人 发 `/set-home`
- 或用 cron deliver 指定群：`feishu:oc_xxx`

### Cron 投递格式
- 私聊：`deliver: "feishu"`
- 指定群：`deliver: "feishu:oc_xxx"`
- 切换：更新 cron job 的 deliver 参数

## 定时任务

工作日 9:00 自动采集 + LLM 分析 + 推送到飞书。

## 执行注意事项

### ⚠️ 脚本执行超时
脚本下载 20+ 个 arXiv PDF 每个约 15-30 秒，总计可能需要 5-8 分钟。**必须使用 600s 超时**（foreground 最大值）：
```bash
python3 /opt/data/scripts/fetch_ai_news.py 2>/tmp/fetch_stderr.txt > /tmp/ai_news_raw.json
# timeout=600
```
300s 超时会在 PDF 下载中途失败。

### 📊 高效论文分析流程
用 `execute_code` 一次性批量读取多篇论文全文，避免逐篇 read_file 的多次工具调用：
1. 先读取 `/opt/data/cron/output/analyzed_papers.json` 获取已分析论文 ID
2. 从候选论文中排除已分析的，筛选 AI 相关论文（排除物理/化学/材料等非 AI 论文）
3. 用 execute_code 循环打印所有候选论文的标题、摘要、全文前3000字符
4. 选出 2 篇最相关的（优先大厂），再用 execute_code 批量读取剩余全文（3000-8000字符段）
5. 基于全文内容撰写深度分析（而非仅凭摘要）
6. 分析完成后，将新论文 ID 追加到 analyzed_papers.json

### 新闻筛选策略
- 100+ 条新闻中精选 6 条要闻：优先产品发布、大额融资、技术突破、行业政策
- 跳过普通广告、非 AI 核心、重复新闻
- 国际新闻翻译成中文标题

## 已知问题

| 问题 | 方案 |
|------|------|
| Google News超时 | 重试3次+备用URL |
| 36氪限速 | 失败跳过 |
| arXiv搜到非LLM论文 | 用ti:标题搜索 |
| 非arXiv无全文 | 基于摘要分析 |
| arXiv XML无机构信息 | 从PDF文本启发式提取（CamelCase分词+噪音过滤+机构关键词库） |
| 论文重复 | quality_key去重（优先保留摘要+单位+日期更完整的记录） |
| 脚本300s超时 | PDF下载需5-8分钟，必须用600s超时 |
| 大厂论文不足 | 1/30是常见比例，无大厂论文时选最相关的AI论文 |

## 外部来源工作流（渐进式披露）

### 触发关键词

| 触发方式 | 示例 | 行为 |
|----------|------|------|
| 发链接 | `https://mp.weixin.qq.com/s/xxx` | 自动识别并收录论文标题 |
| 链接 + 记住 | `记住 https://mp.weixin.qq.com/s/xxx` | 同上 |
| 链接 + 收录 | `收录 https://mp.weixin.qq.com/s/xxx` | 同上 |
| 链接 + 加入日报 | `加入日报 https://mp.weixin.qq.com/s/xxx` | 同上 |
| 查看待分析 | `查看待分析` | 显示 pending_papers.md 内容 |
| 清除待分析 | `清除待分析` | 清空 pending_papers.md |
| 查询 Wiki | `查wiki` / `wiki里有什么` | 读取 ~/wiki/index.md 返回概览 |
| 搜索 Wiki | `查wiki reasoning` | 搜索 ~/wiki/concepts/ 下相关页面 |

### 文件结构
- `/opt/data/scripts/sources/pending_papers.md` — 待分析论文列表（标题+关键词）
- `/opt/data/cron/output/analyzed_sources.json` — 已分析结果（完整论文分析）

### 流程

**1. 用户提供文章链接时**（自动触发）
- 识别公众号/网页链接（mp.weixin.qq.com、openreview.net、arxiv.org 等）
- 自动提取论文标题和关键词
- 追加到 `pending_papers.md`

**2. 做日报时**
- 从 `pending_papers.md` 取标题列表
- 用标题在 arXiv 搜索原文，读 PDF 后自己分析
- 分析完成后：
  a. 从 `pending_papers.md` 删除该条目
  b. 在 `analyzed_sources.json` 追加**完整分析记录**
  c. 如果 `pending_papers.md` 为空则清空文件
  d. **Wiki 写入**：按照 Wiki Writer 步骤（Step 1-6），将论文写入 `~/wiki/` 知识库

**3. analyzed_sources.json 完整格式**
```json
{
  "arxiv_id": "2604.26649",
  "title": "论文标题",
  "date": "2026-04-30",
  "url": "https://arxiv.org/abs/2604.26649",
  "authors": "Author1, Author2, Author3",
  "affiliations": ["Google DeepMind", "Stanford University"],
  "venue": "CVPR 2026",
  "analysis": {
    "problem_background": "问题背景 + 现有方法不足",
    "method_overview": "核心方法概述",
    "key_innovation": "关键创新点",
    "experiment_results": "实验结果（具体数据）",
    "significance": "重要性 + 未来影响"
  },
  "tags": ["reasoning", "multimodal", "selective-thinking"],
  "brief": "一句话中文摘要"
}
```

**4. 渐进式披露规则**
| 用户问题 | 响应方式 |
|----------|----------|
| "最近分析了哪些文章？" | 只显示标题 + brief（不展开分析） |
| "XXX 文章讲了什么？" | 返回完整 analysis（5维度） |
| "帮我找找关于 reasoning 的论文" | 根据 tags 筛选，返回匹配的标题列表 |
| "把 XXX 的分析发给我" | 返回完整 analysis + PDF 链接 |

**5. 禁止事项**
- ❌ 不能照搬公众号/网页内容
- ❌ 不能只列标题不分析
- ❌ 不能在日报中显示所有分析结果（只选2篇）
- ❌ analysis 不能写"见原文"或"略"（必须是完整内容）

## Wiki Writer（知识库写入）— Karpathy LLM Wiki 改造

基于 Karpathy LLM Wiki 模式，每次分析论文后自动写入个人知识库。

### Wiki 路径
`~/wiki/`

### 三层架构
```
wiki/
├── SCHEMA.md           # 领域定义 + 标签约定
├── index.md            # 所有论文/文章的索引
├── log.md              # 操作日志
├── raw/                # 原始素材（不可修改）
│   ├── articles/       # 公众号文章、博客
│   └── papers/         # arXiv PDF 全文
├── entities/           # 实体页（公司、模型、人物）— 带时间线
├── concepts/           # 概念页（技术方法）— 自动累积论文引用
├── comparisons/        # 对比分析
├── queries/            # 存档的查询结果
└── daily-digests/      # 每日日报存档
```

### Wiki Writer 执行步骤（每次分析后自动执行）

**前提：** 先读取 `~/wiki/SCHEMA.md` 了解标签分类和命名规范。

**Step 1: 保存原始素材**
```bash
# PDF 保存到 raw/papers/
cp /tmp/paper_xxx.pdf ~/wiki/raw/papers/{arxiv_id}.pdf
```

**Step 2: 检查并更新实体页**
对每篇论文的作者和机构：
- 搜索 `~/wiki/entities/` 是否已有对应页面
- **已有页面：** 追加新事件到"最新动态"时间线，更新 `updated` 日期
- **无页面：** 如果该实体在 2+ 篇来源中出现，创建新实体页
- 实体页模板：
```markdown
---
title: {实体名称}
created: {日期}
updated: {日期}
type: entity
tags: [{从 SCHEMA 标签分类中选}]
sources: [raw/papers/{arxiv_id}.pdf]
---

# {实体名称}

## 概述
{一句话描述}

## 最新动态
| 日期 | 事件 | 来源 |
|------|------|------|
| {日期} | {事件描述} | 日报 {编号} |

## 相关论文
- [[{paper_page_name}]]

## 关联实体
- [[{related_entity}]]
```

**Step 3: 检查并更新概念页（累积模式）**
对每篇论文的 tags：
- 搜索 `~/wiki/concepts/` 是否已有对应概念页
- **已有页面：** 追加新论文到"论文时间线"列表，更新 `updated` 和 `累积洞察`
- **无页面：** 创建新概念页，写入第一篇论文
- 概念页模板：
```markdown
---
title: {概念名称}
created: {日期}
updated: {日期}
type: concept
tags: [{从 SCHEMA 标签分类中选}]
sources: []
---

# {概念名称}

## 概述
{技术简述}

## 论文时间线
- {日期}: [[{paper_page_name}]] - {一句话摘要}（{机构}）

## 累积洞察
- {从已有论文中总结的趋势/发现}

## 关联概念
- [[{related_concept}]]
```

**Step 4: 更新 index.md**
在对应分类下添加新页面条目，格式：
```
- [[{page_name}]] — {一行摘要}
```
更新顶部的"最后更新"日期和"总页面数"。

**Step 5: 追加 log.md**
```
## [YYYY-MM-DD] ingest | {论文标题}
- 创建 entities/{xxx}.md
- 更新 concepts/{xxx}.md（新增 1 篇论文引用）
- 更新 index.md
```

**Step 6: 保存日报存档**
将今日日报保存到 `~/wiki/daily-digests/YYYY-MM-DD.md`。

### Wiki 查询功能

用户可以随时查询 Wiki：

| 用户问题 | 响应方式 |
|----------|----------|
| "MoE最近有什么新论文？" | 搜索 `concepts/mixture-of-experts.md`，返回论文时间线 |
| "DeepSeek做了什么？" | 读取 `entities/deepseek.md`，返回最新动态 |
| "帮我找关于alignment的论文" | 按标签搜索 concepts/ 下相关页面 |
| "Wiki里有多少篇关于reasoning的论文？" | 汇总所有 reasoning 相关概念页的论文数 |
| "给我一个本周总结" | 汇总 `daily-digests/` 下的日报 |
| "lint一下wiki" | 执行 wiki 健康检查（孤立页、断链、标签审计） |

### 标签自动映射

论文 tags → Wiki 概念页的映射关系：
```
reasoning      → concepts/reasoning.md
alignment      → concepts/alignment.md
fine-tuning    → concepts/fine-tuning.md
rag            → concepts/rag.md
llm-agents     → concepts/llm-agents.md
multimodal     → concepts/multimodal.md
code           → concepts/code-generation.md
safety         → concepts/safety.md
evaluation     → concepts/evaluation.md
scaling        → concepts/scaling.md
```
如果标签没有对应的概念页，自动创建。

### 与现有流程的集成点

| 现有流程 | Wiki 写入时机 |
|----------|-------------|
| cron 日报推送 | 推送完成后执行 Wiki Writer Step 1-6 |
| 导师文章收录 | 分析完成后执行 Wiki Writer Step 1-6 |
| 外部来源分析 | 分析完成后执行 Wiki Writer Step 1-6 |

## 参考项目

- [vigorX777/ai-daily-digest](https://github.com/vigorX777/ai-daily-digest) — Karpathy推荐的90个顶级技术博客 + AI评分系统
- [genggng/hermes-arxiv-agent](https://github.com/genggng/hermes-arxiv-agent) — Hermes论文监控 + 飞书推送 + 网页阅读器

## 文件

- 脚本: `/opt/data/scripts/fetch_ai_news.py`
- 项目仓库: `/opt/projects/ai-daily-research/`
- GitHub: https://github.com/CODE-BULIAO/ai-daily-research
- Wiki 知识库: `~/wiki/`（SCHEMA.md + index.md + log.md + raw/ + entities/ + concepts/）

## 开发经验

### ⚠️ read_file 行号陷阱
hermes_tools 的 read_file() 返回内容带行号前缀。用原生 Python 文件操作替代。

### ⚠️ 多文件同步
脚本存在两个位置，修改后记得同步：`cp 项目脚本 本地脚本`

### ⚠️ Feishu 环境变量
- 环境变量在 Hermes 数据目录的 .env 文件中
- 追加配置后需要重启 gateway 才生效
- PID 1 进程可能需要另开终端运行 restart

### ⚠️ 函数定义了但没调用
`fetch_top_tech_blogs()` 函数定义了但 main() 里从没调用，导致 11 个顶级博客从未被采集。修改脚本后务必检查：新函数是否在 main() 中被调用、新变量是否已定义。

### ⚠️ 文件末尾缺少闭合
多次修改脚本时丢失了 `try/except` 闭合和 `if __name__ == "__main__"` 入口。每次修改后用 `python3 -c "import py_compile; py_compile.compile('file.py', doraise=True)"` 验证语法。
