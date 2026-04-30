# Wiki Schema — 牛马加速器

## Domain
AI/LLM 科研知识库 — 为科研牛马自动积累论文、追踪技术演进、构建个人 Wiki。

## 核心理念
> 基于 Karpathy LLM Wiki 模式改造：自动采集 + 人类转发双轨输入，
> Agent 自动分析并写入 Wiki，日报推给老板，Wiki 给自己积累知识。

## 文件命名规范
- 文件名：小写、连字符、无空格（如 `chain-of-thought.md`、`openai.md`）
- 每个 wiki 页必须有 YAML frontmatter（见下方模板）
- 使用 `[[wikilinks]]` 互链（每页至少 2 个出站链接）
- 更新页面时必须更新 `updated` 日期
- 每个新页面必须添加到 `index.md` 对应分类
- 每次操作必须追加到 `log.md`

## Frontmatter 模板
```yaml
---
title: 页面标题
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query | digest
tags: [从标签分类中选]
sources: [raw/papers/xxx.pdf 或 raw/articles/xxx.md]
---
```

## Tag Taxonomy（标签分类）

### 模型相关
- model, architecture, benchmark, training, inference, scaling

### 技术相关
- reasoning, alignment, fine-tuning, rag, agents, multimodal, code, safety, data, evaluation

### 人/组织相关
- person, company, lab, open-source

### 元相关
- comparison, survey, reproduction, benchmark

**规则：** 标签必须来自以上分类。如需新标签，先添加到此分类，再使用。

## 实体页（entities/）
一个页面对应一个实体（公司、模型、人物）。

```markdown
---
title: OpenAI
created: 2026-04-30
updated: 2026-04-30
type: entity
tags: [company]
sources: []
---

# OpenAI

## 概述
美国AI公司，2015年成立，总部旧金山。

## 最新动态（自动更新）
| 日期 | 事件 | 来源 |
|------|------|------|
| 2026-04-30 | GPT-5 Turbo 发布 | 日报 #128 |

## 相关论文
- [[gpt-5-turbo-eval]]

## 关联实体
- [[Anthropic]]
```

## 概念页（concepts/）— 累积模式
一个页面对应一个技术概念。新论文自动追加。

```markdown
---
title: chain-of-thought（思维链推理）
created: 2026-04-30
updated: 2026-04-30
type: concept
tags: [reasoning]
sources: []
---

# chain-of-thought

## 概述
让LLM逐步推理的技术。

## 论文时间线（自动追加）
- 2026-04-30: [[step-back-prompting]] - 退一步推理（Google DeepMind）

## 累积洞察（Agent 定期更新）
- 核心瓶颈是推理深度 vs 效率的权衡

## 关联概念
- [[reasoning]]
- [[selective-thinking]]
```

## 对比页（comparisons/）
并列分析两个或多个对象。

## 页面创建规则
- **创建页面：** 实体/概念在 2+ 篇来源中出现，或是一篇来源的核心主题
- **更新已有页：** 新来源提到已覆盖的实体/概念
- **不创建页面：** 一笔带过、次要细节、超出领域
- **分割页面：** 超过 200 行时拆分为子主题 + 交叉引用
- **归档页面：** 内容被完全取代时移至 `_archive/`

## 更新策略
当新信息与已有内容矛盾时：
1. 检查日期——新来源通常覆盖旧来源
2. 如确实矛盾，保留两个说法并标注日期和来源
3. 在 frontmatter 标记 `contradictions: [page-name]`

## 日报存档（daily-digests/）
每次日报推送后存档一份到 wiki。

```markdown
# AI 日报 — 2026-04-30

## 要闻
1. ...

## 论文
1. ...

## Wiki 更新
- 创建 entities/openai.md
- 更新 concepts/reasoning.md（新增 1 篇论文引用）
```

## 交叉引用规则
- 每个 wiki 页至少链接 2 个其他页面
- 实体页链接到相关概念页
- 概念页链接到相关实体页和对比页
- 被引用的页面尽量反向链接（形成双向引用）
