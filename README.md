# 🧠 AI Research Wiki · 牛马加速器

> **AI Research Wiki** — Your personal AI research assistant. Collect papers, analyze with 5-dimension deep dive, build a searchable knowledge base. Designed for researchers who want to stay on top of AI/LLM papers without drowning in reading.
> 
> **牛马加速器** — 导师发的公众号文章、论文链接，转发给 Agent 就能自动记录、深度分析、生成日报。还能当个人 Wiki 积累知识，下次直接查！

[![Hermes Agent Skill](https://img.shields.io/badge/Hermes-Agent-Skill-blue)](#hermes-agent-integration)
[![Python 3](https://img.shields.io/badge/Python-3.8+-green)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![arXiv](https://img.shields.io/badge/arXiv-daily-blue)](https://arxiv.org)
[![Wiki](https://img.shields.io/badge/Knowledge-Wiki-green)](https://github.com/CODE-BULIAO/ai-research-wiki)

---

## 🎯 What is this?

**AI Research Wiki** is an AI research assistant that helps you:

| Pain Point | Solution |
|------------|----------|
| 导师转发一堆公众号文章，没时间看 | 转发给 Agent，自动提取文字 + 总结 |
| 老板问最近在看什么，答不上来 | 每天读日报，张口就来 |
| 论文看完了就忘，没有积累 | 自动存档当个人 Wiki，支持搜索 |
| 想让老板觉得你很爱科研 | 每天转发总结好的文章给老板 😎 |

## ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🗞️ **14+ Data Sources** | Chinese RSS + Google News + HN + arXiv + OpenAlex + DBLP + CrossRef + OpenReview + 11 top tech blogs |
| 📄 **Smart Text Extraction** | PDF → PyMuPDF (script, no tokens) · URL → BeautifulSoup (script, no tokens) · LLM only reads what's needed |
| 🔬 **5-Dimension Deep Analysis** | Problem → Innovation → Method → Results → Impact |
| 👤 **Author Affiliation Extraction** | 100+ institution keywords from PDF and metadata |
| 📍 **Venue Annotation** | Shows conference/journal names (NeurIPS, ICML, ACL, etc.) |
| 🏢 **Big Lab Priority** | 30+ focus companies (OpenAI, Google, ByteDance, Huawei, etc.) |
| 📚 **Paper Ingestion** | Send PDF/URL → extract text → save to Wiki → analyze on demand |
| 🔄 **Token-Efficient** | Truncation by operation type: 5K for metadata, 8K for summary, 30K for full analysis |
| 🧠 **Knowledge Base (Wiki)** | Karpathy LLM Wiki style · Auto-indexed · Searchable · Persistent |

## 🏗️ Architecture (v3 — Token-Efficient)

```
Input: PDF / URL / 口头提及
    ↓
Phase 1: 文本提取 (Python脚本, 不消耗token)
├── PDF → PyMuPDF 提取全文 → 存 ~/wiki/raw/papers/
├── URL → BeautifulSoup 提取文字 → 存 ~/wiki/raw/papers/ 或 articles/
└── 提取元数据(标题/作者/来源) → 问用户要做什么
    ↓
Phase 2: 用户选择后执行
├── 📊 深度分析 → 5维度 → analyzed_sources.json + Wiki
├── 📝 快速摘要 → 只读 abstract+conclusion (8K chars)
├── 📰 加入日报候选 → pending_papers.md
└── ❌ 不需要 → 不做任何操作
```

**Key Design**: Script does heavy lifting (PDF/URL extraction), LLM only reads what's needed. Smart truncation: metadata=5K, summary=8K, full analysis=30K chars max.

## 📰 Output Example

```
🤖 AI 日报 | 2026年4月30日

### 🔥 AI 要闻（6条）
1. **谷歌第八代TPU发布，训练推理正式分家**
   - TPU 8t（训练）+ TPU 8i（推理），首次明确"分家"

### 📄 论文精选（2篇，深度解析）
📌 **Turning the TIDE: Cross-Architecture Distillation for Diffusion LLMs**
- 👤 Gongbo Zhang 等 | 北京大学、浙江大学
- 📍 arXiv | cs.CL, cs.AI, cs.LG
- 🔬 创新点深度解析：
  1. **问题背景**：dLLM 参数量大，推理成本高...
  2. **核心方法**：TIDE 框架包含三个模块...
  3. **关键创新点**：首次解决跨架构蒸馏问题...

### 📊 今日趋势
一句话总结...
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install --break-system-packages pymupdf beautifulsoup4 lxml lark-oapi websockets
```

### 2. Clone

```bash
git clone https://github.com/CODE-BULIAO/ai-research-wiki.git
cd ai-research-wiki
```

### 3. Run Manually

```bash
python3 fetch_ai_news.py
```

### 4. Set Up Cron Job (Hermes Agent)

```python
cronjob(
    action="create",
    name="AI Research Wiki - Daily Digest",
    schedule="0 9 * * 1-5",  # Weekdays 9:00 AM
    deliver="feishu:oc_xxx"   # Push to Feishu group
)
```

## 📁 Project Structure

```
ai-research-wiki/
├── README.md                # Project overview
├── SKILL.md                 # Hermes Agent Skill definition
├── LICENSE                  # MIT
├── fetch_ai_news.py         # Core collection script (14+ sources)
└── wiki/                    # Wiki templates
    ├── SCHEMA.md            # Schema definition
    ├── index.md             # Knowledge index
    └── log.md               # Operation log

Runtime data:
~/wiki/                      # Working knowledge base
├── raw/papers/              # Paper full text
├── raw/articles/            # Article text
├── concepts/                # Concept pages (auto-accumulated)
├── entities/                # Entity pages (with timeline)
└── daily-digests/           # Daily digest archives
```

## 📊 Data Sources (14+)

### Chinese News RSS
| Source | Status |
|--------|--------|
| 雷峰网 | ✅ |
| 量子位 | ✅ |
| 极客公园 | ✅ |
| 钛媒体 | ✅ |
| IT之家 | ✅ |
| 36氪 | ⚠️ Rate limited |

### International
| Source | Focus |
|--------|-------|
| Google News | Global aggregation |
| Hacker News | Tech community |

### Top Tech Blogs (Karpathy Recommended)
Simon Willison · Antirez · GWERN · Paul Graham · Dan Luu · Julia Evans · Mitchell Hashimoto · Overreacted · matklad · Minimaxir · GeoHot

### Academic Sources (6)
| Source | Coverage |
|--------|----------|
| arXiv | Preprints (most AI papers) |
| OpenAlex | Journals + Conferences |
| DBLP | Conference proceedings |
| CrossRef | Publisher papers (DOI) |
| OpenReview | NeurIPS/ICLR/ICML |
| Google Scholar | Comprehensive |

## 📚 Paper Ingestion

Send a paper via PDF or URL:

| Trigger | Action |
|---------|--------|
| Send PDF attachment | Extract text → Save → Ask user |
| Send URL (arxiv/openreview) | Download PDF → Extract → Save → Ask user |
| Send URL (blog/article) | Extract text via BeautifulSoup → Save → Ask user |
| Mention paper title | Search → Download → Save → Ask user |
| "收录..." / "加入日报..." | Save to pending only |

**User chooses what to do:**
1. 📊 Deep analysis (5-dimension, write to Wiki)
2. 📝 Quick summary (abstract + conclusion only)
3. 📰 Add to daily digest candidates
4. ❌ No thanks

## 📝 Changelog

### v3.0.0 (2026-05-13)
- 🧠 **Knowledge-first design**: Any analyzed paper is saved to Wiki permanently
- ⏸️ **Stop-and-ask**: Paper detection → save text → ask user what to do (saves tokens)
- 🔍 **Smart retrieval**: Check Wiki before answering follow-up questions
- ✂️ **Text truncation**: 5K for metadata, 8K for summary, 30K for full analysis
- 🌐 **URL text extraction**: BeautifulSoup for web pages (no PDF download needed)
- 📋 **Unified trigger matrix**: PDF/URL/oral → all follow same get→save→ask flow

### v2.0.0 (2026-05-06)
- 🏗️ Architecture restructure: PDF full text stored in `raw/papers/`
- ⚡ Reduced collection: News 100→50, Papers 20→~14
- 🗑️ Removed inline `full_text` field, use `raw_text_path`

### v1.2.0 (2026-04-30)
- ✨ CrossRef + OpenReview sources
- ✨ External article ingestion + progressive disclosure
- 🔄 Feishu push (replaced WeChat)

### v1.1.0 (2026-04-30)
- ✨ 11 Karpathy-recommended tech blogs
- ✨ Big lab priority sorting
- 📄 PDF affiliation extraction enhancement

### v1.0.0 (2026-04-30)
- ✨ Initial version with 11 data sources
- 📄 arXiv PDF full text extraction
- 🔬 5-dimension deep analysis

## 🤖 Hermes Agent Integration

This project is a [Hermes Agent](https://github.com/NousResearch/hermes-agent) Skill.

### What is Hermes Agent?
An open-source AI agent framework supporting:
- Multi-platform messaging (Feishu, WeChat, Telegram, Discord)
- Cron job scheduling
- Skill system
- Tool calling and code execution

### How to Use
1. Install Hermes Agent
2. Put `SKILL.md` in the skills directory
3. Configure Feishu/WeChat push
4. Create a cron job for daily digest

## 🙏 Acknowledgments

Powered by **Xiaomi MiMo 100T** for AI capabilities.

> Xiaomi MiMo 100T provides high-quality Chinese language understanding and generation for news summarization, paper analysis, and innovation extraction.

**Token Source**: [Xiaomi MiMo Platform](https://platform.xiaomimimo.com?ref=P67V88)

Thanks to Xiaomi MiMo team for supporting the open source community! 🎉

---

## 🤝 Contributing

Issues and PRs welcome!

## 📄 License

[MIT](LICENSE)

---

**Made with ❤️ by Yiwen**
