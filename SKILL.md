---
name: ai-daily-research
description: >
  自动采集、分析并生成每日 AI 新闻日报 + 论文深度研究。覆盖国内外新闻、arXiv/OpenAlex/DBLP 论文。
  支持 PDF 全文提取、作者单位分析、创新点深度解析。大厂论文优先。工作日自动推送到飞书。
version: 1.2.0
author: CODE-BULIAO
license: MIT
tags: [AI, News, Papers, Daily, Research, ArXiv, OpenAlex, LLM]
github: https://github.com/CODE-BULIAO/ai-daily-research
---

# AI Daily Research

自动采集、分析并生成每日 AI 新闻日报 + 论文深度研究的 Hermes Agent Skill。

## 架构

```
脚本采集 (Python) → JSON → LLM总结 → 飞书推送
```

**关键设计**：脚本负责数据采集+预处理，LLM负责智能总结+格式化。分离关注点。

## 数据源

| 类型 | 来源 | 备注 |
|------|------|------|
| 🇨🇳 中文 | 雷峰网/量子位/极客公园/钛媒体/IT之家/36氪 | 36氪限速 |
| 🌍 英文 | Google News(重试机制)/HN(points>30) | |
| ✍️ 博客 | 11个Karpathy推荐顶级技术博客(Simon Willison/GWERN/Paul Graham等) | RSS |
| 📄 学术 | arXiv(PDF全文)+OpenAlex(作者单位)+DBLP(会议) | |

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

## 外部来源工作流

当用户提供微信/网页文章链接时：
1. **提取论文标题** — 从文章中提取论文名称和关键词
2. **保存为搜索列表** — 存到 `/opt/data/scripts/sources/` 目录
3. **做日报时搜索原文** — 用标题在 arXiv 搜索，读 PDF 后自己分析
4. **禁止直接复制** — 不能照搬公众号内容，必须基于原文独立分析

## 参考项目

- [vigorX777/ai-daily-digest](https://github.com/vigorX777/ai-daily-digest) — Karpathy推荐的90个顶级技术博客 + AI评分系统
- [genggng/hermes-arxiv-agent](https://github.com/genggng/hermes-arxiv-agent) — Hermes论文监控 + 飞书推送 + 网页阅读器

## 文件

- 脚本: `/opt/data/scripts/fetch_ai_news.py`
- 项目仓库: `/opt/projects/ai-daily-research/`
- GitHub: https://github.com/CODE-BULIAO/ai-daily-research

## 开发经验

### ⚠️ read_file 行号陷阱
hermes_tools 的 read_file() 返回内容带行号前缀。用原生 Python 文件操作替代。

### ⚠️ 多文件同步
脚本存在两个位置，修改后记得同步：`cp 项目脚本 本地脚本`

### ⚠️ Feishu 环境变量
- 环境变量在 Hermes 数据目录的 .env 文件中
- 追加配置后需要重启 gateway 才生效
- PID 1 进程可能需要另开终端运行 restart
