---
name: ai-daily-research
description: >
  自动采集、分析并生成每日 AI 新闻日报 + 论文深度研究。覆盖国内外新闻、arXiv/OpenAlex/DBLP 论文。
  支持 PDF 全文提取、作者单位分析、创新点深度解析。大厂论文优先。每天早上9点自动推送到微信。
version: 1.1.0
author: CODE-BULIAO
license: MIT
tags: [AI, News, Papers, Daily, Research, ArXiv, OpenAlex, LLM]
github: https://github.com/CODE-BULIAO/ai-daily-research
---

# AI Daily Research

自动采集、分析并生成每日 AI 新闻日报 + 论文深度研究的 Hermes Agent Skill。

## 架构

```
脚本采集 (Python) → JSON → LLM总结 → 微信推送
```

**关键设计**：脚本负责数据采集+预处理，LLM负责智能总结+格式化。分离关注点。

## 安装依赖

```bash
pip install --break-system-packages pymupdf
```

## 数据源

| 类型 | 来源 | 备注 |
|------|------|------|
| 🇨🇳 中文 | 雷峰网/量子位/极客公园/钛媒体/IT之家/36氪 | 36氪限速 |
| 🌍 英文 | Google News(重试机制)/HN(points>30) | |
| 📄 学术 | arXiv(PDF全文)+OpenAlex(作者单位)+DBLP(会议) | |

## 大厂论文优先

脚本标记 is_focus_company，论文排序时大厂优先。

**国际**: OpenAI, Google DeepMind, Anthropic, Meta AI, Microsoft, Apple, Amazon, NVIDIA, xAI, Mistral
**国内**: 百度, 阿里, 腾讯, 字节, 华为, 美团, 小米, 商汤, Kimi, 智谱AI, DeepSeek, MiniMax, 蚂蚁

## 输出格式

- 📰 AI 要闻 6条（精选，不分国内外）
- 📄 论文 3-5篇（大厂优先，含全部作者单位 + 创新点深度解析5维度）
- 📊 趋势 1句话

## 定时任务

工作日 9:00 推送到微信。

## 已知问题

| 问题 | 方案 |
|------|------|
| Google News超时 | 重试3次+备用URL |
| 36氪限速 | 失败跳过 |
| arXiv搜到非LLM论文 | 用ti:标题搜索 |
| 非arXiv无全文 | 基于摘要分析 |
| GitHub推送 | PAT token认证 |

## 参考项目

- [vigorX777/ai-daily-digest](https://github.com/vigorX777/ai-daily-digest) — Karpathy推荐的90个顶级技术博客 + AI评分系统
  - 启发：添加顶级技术博客RSS源、AI三维度评分（相关性+质量+时效性）、分类标签

## 文件

- 脚本: `/opt/data/scripts/fetch_ai_news.py`
- 项目仓库: `/opt/projects/ai-daily-research/`
- GitHub: https://github.com/CODE-BULIAO/ai-daily-research

## 开发经验

### ⚠️ read_file 行号陷阱
hermes_tools 的 `read_file()` 返回内容带行号前缀（如 `1|#!/usr/bin/env python3`）。
用这些内容做 patch/replace 会失败，因为目标字符串不匹配。

**解决方案**：用原生 Python 文件操作替代 hermes_tools：
```python
with open(path) as f:
    content = f.read()
content = content.replace(old, new)
with open(path, 'w') as f:
    f.write(content)
```

### ⚠️ 多文件同步
脚本存在两个位置：
- `/opt/projects/ai-daily-research/scripts/fetch_ai_news.py` (GitHub 仓库)
- `/opt/data/scripts/fetch_ai_news.py` (本地运行)

修改后记得同步：`cp 项目脚本 本地脚本`

### GitHub 推送流程
```bash
git remote set-url origin https://CODE-BULIAO:<PAT>@github.com/CODE-BULIAO/ai-daily-research.git
git push
git remote set-url origin https://github.com/CODE-BULIAO/ai-daily-research.git  # 清理token
```
