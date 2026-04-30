---
name: ai-daily-research
description: >
  自动采集、分析并生成每日 AI 新闻日报。覆盖国内/国际新闻、arXiv/OpenAlex/DBLP 论文。
  支持 PDF 全文提取、作者单位分析、创新点深度解析。每天早上9点自动推送到微信。
version: 5.0.0
author: Hermes Agent
tags: [AI, News, Papers, Daily, Digest, ArXiv, OpenAlex]
---

# AI Daily Research 系统

## 架构概览

```
数据采集层                    分析层                      输出层
├── 中文RSS (6站)             ├── LLM智能总结             ├── 微信推送
├── Google News               ├── 论文全文分析             ├── 本地文件
├── Hacker News               ├── 创新点深度解析           └── JSON存档
├── arXiv (含PDF下载)          └── 趋势分析
├── OpenAlex (含作者单位)
└── DBLP (含会议信息)
```

**关键设计决策：脚本只负责采集+提取，输出JSON；LLM负责智能总结+格式化。**

## 输出格式

### 1. 🔥 AI 要闻 (6条)
- 从约100条新闻中精选最重要的6条
- **不区分国内/国外**，统一按重要性排序
- 国际新闻翻译成中文
- 每条包含具体数字、公司名、产品名

### 2. 📄 论文精选 (3-5篇)
**必须是大语言模型（LLM）相关的论文。**

判断标准（至少满足一项）：
- 标题/摘要包含：LLM, language model, GPT, transformer, diffusion LLM, SLM, agent, chat, instruction tuning, RLHF, reasoning, chain-of-thought, RAG, fine-tuning, alignment, safety, benchmark
- 研究主题涉及：语言模型训练/推理/部署/优化/安全/评估/应用

**跳过**：纯数学优化、凸优化、信号处理、医疗AI、教育研究、社会学等

每篇包含：
- 英文原标题 + 中文翻译标题
- 作者 & 单位 (从PDF/元数据提取)
- 发表位置 (会议/期刊)
- 🔬 **创新点深度解析**（5个维度，每篇至少5句话）：
  1. 问题背景：解决什么问题？为什么重要？
  2. 现有方法的不足
  3. 核心方法
  4. **关键创新点**（与现有方法的本质区别，最重要）
  5. 实验结果
- 链接

### 3. 📊 今日趋势
一句话总结

## 重点跟踪公司

### 🌍 国际大厂
OpenAI, Google DeepMind, Anthropic, Meta AI/FAIR, Microsoft Research, Apple AI, Amazon AI/AWS, NVIDIA, xAI, Cohere, Stability AI, Mistral AI, Inflection AI

### 🇨🇳 国内大厂
百度, 阿里巴巴/阿里云, 腾讯, 字节跳动/豆包, 华为, 美团, 小米, 商汤, 月之暗面/Kimi, 智谱AI/GLM, 百川智能, 零一万物/01.AI, MiniMax, 深度求索/DeepSeek, 蚂蚁集团, 京东, 网易, 快手, 科大讯飞, 昆仑万维

> 论文筛选时优先选择来自以上公司的研究，确保日报覆盖行业前沿动态。

## 数据源配置

### 中文新闻 RSS
| 来源 | 地址 | AI相关度 |
|------|------|----------|
| 雷峰网 | leiphone.com/feed | ⭐⭐⭐⭐⭐ AI/机器人 |
| 量子位 | qbitai.com/feed | ⭐⭐⭐⭐⭐ AI垂直 |
| 极客公园 | geekpark.net/rss | ⭐⭐⭐⭐ 科技+AI |
| 钛媒体 | tmtpost.com/rss | ⭐⭐⭐⭐ 科技商业 |
| IT之家 | ithome.com/rss/ | ⭐⭐⭐ 综合科技 |
| 36氪 | 36kr.com/feed | ⭐⭐⭐⭐⭐ 头部科技(限速) |

### 国际新闻
| 来源 | 地址 | 备注 |
|------|------|------|
| Google News | news.google.com/rss/search?q=AI... | 需重试机制 |
| Hacker News | hn.algolia.com API | points>30 才入选 |

### 学术来源
| 来源 | 特点 | 额外信息 |
|------|------|----------|
| arXiv | 最新预印本 | **只搜LLM相关关键词**，下载PDF提取全文、作者单位、comment(会议信息) |
| OpenAlex | 已发表论文 | venue(会议/期刊名)、作者机构、引用数 |
| DBLP | CS会议论文 | 会议简称、论文类型 |

## ⚠️ 关键教训（踩过的坑）

### arXiv 搜索必须精准
- ❌ 不要用 `cat:cs.AI OR cat:cs.CL OR cat:cs.LG`（太宽泛，会抓到凸优化、信号处理等）
- ✅ 用 `ti:language model OR ti:LLM OR ti:transformer OR ti:GPT` 等标题关键词搜索
- ✅ 分4个方向搜索：LLM-Core / LLM-Training / LLM-Agent / LLM-Eval

### Google News 必须有重试
- 首次请求偶发超时，需要3次重试 + 备用URL

### 36氪 RSS 限速
- 频繁请求会触发验证码/CAPTCHA，控制请求频率

### Semantic Scholar 不要用
- 用户明确不需要，查询慢且对新论文覆盖率低

### 不要按渠道分组
- ❌ 分"Google News"、"Hacker News"、"中文RSS"等渠道展示
- ✅ 全部合并为统一新闻池，按重要性排序

### PDF 全文提取
- 使用 pymupdf 提取前4页（约8K字符）
- 非arXiv论文（OpenAlex/DBLP）可能无全文，用abstract代替

## 脚本位置

- **采集脚本**: `/opt/data/scripts/fetch_ai_news.py`
- **输出目录**: `/opt/data/cron/output/`
- **原始JSON**: `ai_raw_YYYYMMDD.json`

## 定时任务

- **Job ID**: 4a80f1af9a81
- **Schedule**: 每天 09:00 (Asia/Shenzhen)
- **Delivery**: weixin
- **Model**: 默认

## 依赖

- Python 3 + pymupdf (PDF文本提取)
- 标准库: urllib, xml, json, re

## 已知限制 & 踩坑

1. **36氪 RSS 限速**：频繁请求会触发验证码，单次运行不要重复请求
2. **Google News 偶发超时**：必须加 retry 逻辑 + 备选 query URL
3. **中文 SPA 平台无法爬取**：小红书、微博、知乎、即刻、机器之心（已关停RSS）全部是 SPA，curl 只能拿到空壳
4. **arXiv 搜索关键词**：用 `ti:` 前缀搜标题（如 `ti:language+model`）比 `cat:` 搜分类更精准，避免捞到不相关的论文
5. **PDF 提取限前4页**：约 8K 字符，足够 LLM 做摘要但不够全文分析
6. **非 arXiv 论文无全文**：OpenAlex/DBLP 的论文只有摘要，没有 PDF 全文
7. **GitHub PAT 安全**：push 后必须 `git remote set-url origin` 清除 token
8. **论文筛选**：早期用 `cat:cs.AI+OR+cat:cs.CL` 会捞到大量非 LLM 论文（凸优化、信号处理等），必须用更具体的查询词

## 参考工具

- ChatPaper (19.4k⭐) - 论文批量摘要
- genggng/hermes-arxiv-agent (50⭐) - Hermes arXiv技能
- paperqa - LLM论文问答
- arxiv-sanity-lite (1.6k⭐) - 论文推荐
