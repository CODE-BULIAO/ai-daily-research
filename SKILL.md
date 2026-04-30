---
name: ai-daily-digest
description: >
  自动生成每日 AI 新闻日报。覆盖国内外新闻、arXiv/OpenAlex/DBLP 论文。
  支持 PDF 全文提取、作者单位分析、创新点深度解析。
version: 1.0.0
author: Yiwen
license: MIT
tags: [AI, News, Papers, Daily, Digest, ArXiv, OpenAlex, LLM]
---

# AI Daily Digest

自动采集、分析并生成每日 AI 新闻日报的 Hermes Agent Skill。

## 功能特性

- 🗞️ **11 个数据源**：6 个中文 RSS + Google News + Hacker News + arXiv + OpenAlex + DBLP
- 📄 **论文全文分析**：自动下载 arXiv PDF，提取全文内容
- 🔬 **创新点深度解析**：基于全文分析论文的问题背景、方法、创新点
- 👤 **作者单位提取**：从 PDF 和元数据中提取作者所属机构
- 📍 **发表位置标注**：显示会议/期刊名称
- 🤖 **LLM 智能总结**：自动筛选、翻译、总结，生成高质量日报

## 数据源

| 类型 | 来源 | 内容 |
|------|------|------|
| 🇨🇳 中文 | 雷峰网、量子位、极客公园、钛媒体、IT之家、36氪 | 国内 AI 动态 |
| 🌍 英文 | Google News、Hacker News | 国际 AI 动态 |
| 📄 学术 | arXiv（含 PDF 全文） | 最新预印本 |
| 📍 学术 | OpenAlex（含作者单位） | 已发表论文 |
| 📍 学术 | DBLP（含会议信息） | CS 会议论文 |

## 安装

### 依赖
```bash
pip install pymupdf
```

### 脚本
```bash
cp scripts/fetch_ai_news.py /opt/data/scripts/
chmod +x /opt/data/scripts/fetch_ai_news.py
```

## 使用

### 手动运行
```bash
python3 scripts/fetch_ai_news.py
```

### 定时任务（Hermes Agent）
```python
cronjob(
    action="create",
    name="AI Daily Digest",
    schedule="0 9 * * 1-5",  # 工作日 9:00
    prompt="运行脚本并生成日报...",
    deliver="weixin"
)
```

## 输出格式

### 📰 新闻（6 条）
精选最重要的 6 条 AI 新闻，不分国内外。

### 📄 论文（3-5 篇）
每篇包含：
- 英文标题 + 中文翻译
- 作者 & 单位
- 发表位置（会议/期刊）
- 创新点深度解析（5 个维度）

### 📊 趋势
一句话总结当日趋势。

## 配置

编辑 `config/sources.yaml` 可以：
- 启用/禁用数据源
- 调整论文搜索关键词
- 修改输出格式

## License

MIT
