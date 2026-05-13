# SCHEMA.md — 领域定义 + 标签约定

> 本文件定义 Wiki 的分类体系和命名规范。Agent 在创建/更新页面时必须遵循。

## 分类体系

### 论文 (Papers)
- 存放位置: `concepts/` (按技术概念) + `entities/` (按作者/机构)
- 文件格式: Markdown, YAML frontmatter
- 命名: `kebab-case` (如 `mixture-of-experts.md`)

### 实体 (Entities)
- 公司/机构: `entities/{name}.md`
- 人物: `entities/{name}.md` (姓名全小写, 多词用连字符)
- 模型: `entities/{name}.md`

### 概念 (Concepts)
- 技术方法: `concepts/{name}.md`
- 一篇论文可以关联多个概念
- 概念页按时间线累积论文引用

## 标签约定

### 大类标签
| 标签 | 说明 |
|------|------|
| `llm` | 大语言模型相关 |
| `training` | 训练方法（RLHF/DPO/GRPO等） |
| `reasoning` | 推理能力 |
| `multimodal` | 多模态（视觉+语言等） |
| `agents` | AI Agent / 工具使用 |
| `safety` | 安全、对齐 |
| `evaluation` | 评估、基准测试 |
| `education` | 教育应用 |
| `code` | 代码生成 |
| `rag` | 检索增强生成 |
| `vision` | 计算机视觉 |
| `robotics` | 机器人 |
| `nlp` | 自然语言处理 |
| `svg` | SVG / 可视化 |
| `scaling` | 缩放定律 |
| `fine-tuning` | 微调 |

### 子标签
可在大类标签后加子标签细化，如: `llm-gpt4`, `training-grpo`, `reasoning-cot`

## 命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| 概念页 | `concepts/{kebab-case}.md` | `concepts/in-context-learning.md` |
| 实体页 | `entities/{kebab-case}.md` | `entities/deepseek.md` |
| 原始论文 | `raw/papers/{arxiv_id}.pdf` | `raw/papers/2503.07429.pdf` |
| 原始文章 | `raw/papers/{id}.txt` | `raw/papers/file_a1b2c3d4.txt` |
| 日报存档 | `daily-digests/YYYY-MM-DD.md` | `daily-digests/2026-05-13.md` |

## 页面模板

### 概念页 (Concept Page)
```markdown
---
title: {概念名称}
created: {日期}
updated: {日期}
type: concept
tags: [{标签列表}]
---

# {概念名称}

## 概述
{一句话描述}

## 论文时间线
- {日期}: [[{paper_page_name}]] - {一句话摘要}（{机构}）

## 累积洞察
- {从已有论文中总结的趋势/发现}

## 关联概念
- [[{related_concept}]]
```

### 实体页 (Entity Page)
```markdown
---
title: {实体名称}
created: {日期}
updated: {日期}
type: entity
tags: [{标签列表}]
---

# {实体名称}

## 概述
{一句话描述}

## 最新动态
| 日期 | 事件 | 来源 |
|------|------|------|
| {日期} | {事件描述} | 论文 {arxiv_id} |

## 相关论文
- [[{paper_page_name}]] — {一句话摘要}

## 关联实体
- [[{related_entity}]]
```

### 论文分析 (Paper Analysis)
存储在 `analyzed_sources.json`，格式:
```json
{
  "arxiv_id": "2503.07429",
  "title": "论文标题",
  "date": "2025-03-10",
  "url": "https://arxiv.org/abs/2503.07429",
  "authors": "Author1, Author2",
  "affiliations": ["机构1"],
  "venue": "期刊/会议名",
  "analysis": {
    "problem_background": "...",
    "method_overview": "...",
    "key_innovation": "...",
    "experiment_results": "...",
    "significance": "..."
  },
  "tags": ["svg", "llm", "education"],
  "brief": "一句话中文摘要"
}
```
