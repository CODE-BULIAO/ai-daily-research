# 🤖 AI Daily Research

> **Hermes Agent Skill** — 每日自动采集 AI 新闻 + AI 论文，深度分析后推送到飞书

[![Hermes Agent Skill](https://img.shields.io/badge/Hermes-Agent-Skill-blue)](#hermes-agent-integration)
[![Python 3](https://img.shields.io/badge/Python-3.8+-green)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ 特性

| 功能 | 说明 |
|------|------|
| 🗞️ **14+ 数据源** | 中文RSS + Google News + HN + arXiv + OpenAlex + DBLP + CrossRef + OpenReview + 11个顶级博客 |
| 📄 **论文全文分析** | 自动下载 arXiv PDF，提取全文内容进行深度分析 |
| 🔬 **创新点深度解析** | 5维度分析：问题背景→现有不足→核心方法→关键创新→实验结果 |
| 👤 **作者单位提取** | 从 PDF 和元数据中提取 100+ 机构关键词匹配 |
| 📍 **发表位置标注** | 显示会议/期刊名称（NeurIPS、ICML、ACL 等） |
| 🏢 **大厂论文优先** | 30+ 重点公司（OpenAI、Google、字节、华为等）论文优先展示 |
| 📚 **外部文章收录** | 发链接自动提取论文标题，加入待分析列表 |
| 🔄 **渐进式披露** | 完整分析存档，平时只显示标题，用户问才展开 |

## 📰 输出示例

```
🤖 AI 日报 | 2026年4月30日

### 🔥 AI 要闻（6条）
1. **谷歌第八代TPU发布，训练推理正式分家**
   - TPU 8t（训练）+ TPU 8i（推理），首次明确"分家"
   - 谷歌VP：AI智能体时代需要针对性优化的芯片

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

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install --break-system-packages pymupdf lark-oapi websockets
```

### 2. 下载脚本

```bash
git clone https://github.com/CODE-BULIAO/ai-daily-research.git
cd ai-daily-research
```

### 3. 手动运行

```bash
python3 scripts/fetch_ai_news.py
```

### 4. 定时任务（Hermes Agent）

```python
# 在 Hermes Agent 中创建定时任务
cronjob(
    action="create",
    name="AI Daily Research",
    schedule="0 9 * * 1-5",  # 工作日 9:00
    deliver="feishu:oc_xxx"  # 推送到飞书群
)
```

## 📁 项目结构

```
ai-daily-research/
├── README.md                # 项目介绍
├── SKILL.md                 # Hermes Agent Skill 定义（完整流程）
├── LICENSE                  # MIT 协议
├── scripts/
│   └── fetch_ai_news.py     # 核心采集脚本（14+ 数据源）
├── config/
│   └── sources.yaml         # 数据源配置
└── examples/
    └── sample_output.md     # 日报示例
```

## 📊 数据源详情（14+）

### 中文新闻 RSS
| 来源 | 特点 | 状态 |
|------|------|------|
| 雷峰网 | AI/机器人专业报道 | ✅ |
| 量子位 | AI 垂直深度 | ✅ |
| 极客公园 | 科技+AI | ✅ |
| 钛媒体 | 科技商业 | ✅ |
| IT之家 | 综合科技 | ✅ |
| 36氪 | 头部科技媒体 | ⚠️ 限速 |

### 国际新闻
| 来源 | 特点 |
|------|------|
| Google News | 全球媒体聚合 |
| Hacker News | 技术社区热议 |

### 顶级技术博客（Karpathy 推荐）
| 来源 | 特点 |
|------|------|
| Simon Willison | LLM 应用专家 |
| Antirez (Redis 作者) | 系统/编程 |
| GWERN | AI 深度分析 |
| Paul Graham | 创业/技术思考 |
| Dan Luu | 系统/性能 |
| Julia Evans | 编程探索 |
| Mitchell Hashimoto | 基础设施 |
| Overreacted (Dan Abramov) | React/前端 |
| matklad | Rust/工具链 |
| Minimaxir | AI 实验 |
| GeoHot | AI/创业 |

### 学术来源（6个）
| 来源 | 覆盖范围 | 优势 |
|------|---------|------|
| arXiv | 预印本（大部分 AI 论文） | 有 PDF 全文 |
| OpenAlex | 期刊+会议（引用数据） | 有作者单位 |
| DBLP | 会议论文集 | 会议信息全 |
| CrossRef | 出版商论文（DOI解析） | 覆盖最广 |
| OpenReview | NeurIPS/ICLR/ICML | 顶会原文 |
| Google Scholar | 综合学术搜索 | 补充渠道 |

### 🏢 重点跟踪公司（30+）

**国际大厂**：OpenAI, Google DeepMind, Anthropic, Meta AI, Microsoft, Apple, Amazon, NVIDIA, xAI, Cohere, Mistral AI 等

**国内大厂**：百度, 阿里, 腾讯, 字节/豆包, 华为, 美团, 小米, 商汤, 月之暗面/Kimi, 智谱AI/GLM, DeepSeek, MiniMax, 蚂蚁集团, 京东, 网易, 快手, 科大讯飞, 昆仑万维 等

> 💡 论文筛选优先选择来自以上公司的研究，确保日报覆盖行业前沿动态。

## 📚 外部文章收录

### 触发方式

| 触发方式 | 示例 | 行为 |
|----------|------|------|
| 发链接 | `https://mp.weixin.qq.com/s/xxx` | 自动识别并收录论文标题 |
| 链接 + 记住 | `记住 https://mp.weixin.qq.com/s/xxx` | 同上 |
| 链接 + 收录 | `收录 https://mp.weixin.qq.com/s/xxx` | 同上 |
| 链接 + 加入日报 | `加入日报 https://mp.weixin.qq.com/s/xxx` | 同上 |
| 查看待分析 | `查看待分析` | 显示待分析论文列表 |
| 清除待分析 | `清除待分析` | 清空待分析列表 |

### 渐进式披露

- **平时查询**：只显示标题 + 一句话摘要（防止重复）
- **用户追问**：展开完整 5 维度分析（问题背景/核心方法/关键创新/实验结果/重要性）
- **按标签筛选**：根据关键词（reasoning/multimodal 等）筛选相关论文

## 🔄 工作流程

```
用户给链接 → 自动提取论文标题 → 存入 pending_papers.md
    ↓
做日报时搜 arXiv 原文 → 读 PDF → 完整分析（5维度）
    ↓
从 pending 删除 → 存入 analyzed_sources.json
    ↓
飞书推送日报 → 同时存档完整分析
```

## 🤖 Hermes Agent 集成

本项目是一个 [Hermes Agent](https://github.com/NousResearch/hermes-agent) Skill。

### 什么是 Hermes Agent？

Hermes Agent 是一个开源的 AI 代理框架，支持：
- 多平台消息推送（飞书、微信、Telegram、Discord）
- 定时任务调度
- 技能（Skill）系统
- 工具调用和代码执行

### 如何使用

1. 安装 Hermes Agent
2. 将 `SKILL.md` 放入 skills 目录
3. 配置飞书/微信推送
4. 创建定时任务，自动推送日报

## 📝 更新日志

### v1.2.0 (2026-04-30)
- ✨ 新增 CrossRef + OpenReview 学术来源
- ✨ 新增外部文章收录 + 渐进式披露工作流
- ✨ 新增触发关键词（发链接自动收录）
- 🔄 飞书推送（替代微信）
- 🔄 数据源从 11 个扩展到 14+

### v1.1.0 (2026-04-30)
- ✨ 新增 11 个 Karpathy 推荐顶级技术博客
- ✨ 大厂论文优先排序
- 📄 PDF 机构提取增强（CamelCase分词、噪音过滤）

### v1.0.0 (2026-04-30)
- ✨ 初始版本
- 🗞️ 支持 11 个数据源
- 📄 支持 arXiv PDF 全文提取
- 🔬 支持创新点深度解析

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📄 License

[MIT](LICENSE)

---

## 🙏 Acknowledgments

本项目的运行由 **小米 MiMo 100T** 提供算力支持。

> MiMo 100T 是小米推出的大语言模型，具备强大的中文理解与生成能力，为本项目的新闻摘要、论文分析、创新点解析等核心功能提供了高质量的 AI 能力支撑。

**Token 来源**：[小米 MiMo 平台](https://platform.xiaomimimo.com?ref=P67V88)

感谢小米 MiMo 团队对开源社区的支持！🎉

---

**Made with ❤️ by Yiwen**
