# 🦞 AI Daily Digest

> 自动采集、分析并生成每日 AI 新闻日报 —— 覆盖国内外新闻 + 学术论文深度解析

[![Hermes Agent Skill](https://img.shields.io/badge/Hermes-Agent-Skill-blue)](#hermes-agent-integration)
[![Python 3](https://img.shields.io/badge/Python-3.8+-green)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ 特性

| 功能 | 说明 |
|------|------|
| 🗞️ **11 个数据源** | 6 个中文 RSS + Google News + Hacker News + arXiv + OpenAlex + DBLP |
| 📄 **论文全文分析** | 自动下载 arXiv PDF，提取全文内容进行深度分析 |
| 🔬 **创新点深度解析** | 基于全文分析论文的问题背景、方法、创新点、实验结果 |
| 👤 **作者单位提取** | 从 PDF 和元数据中提取作者所属机构 |
| 📍 **发表位置标注** | 显示会议/期刊名称（NeurIPS、ICML、ACL 等） |
| 🤖 **LLM 智能总结** | 自动筛选、翻译、总结，生成高质量日报 |

## 📰 输出示例

```
🦞 AI 日报 | 2026年4月30日

### 🔥 AI 要闻（6条）

1. **谷歌第八代TPU发布，训练推理正式分家**
   - TPU 8t（训练）+ TPU 8i（推理），首次明确"分家"
   - 谷歌VP：AI智能体时代需要针对性优化的芯片
   - 直接对标英伟达，改变AI芯片竞争格局

2. **亚马逊给Anthropic 250亿，给OpenAI 500亿**
   - ...

### 📄 论文精选（3-5篇）

📌 **Turning the TIDE: Cross-Architecture Distillation for Diffusion LLMs**
扩散大语言模型的跨架构蒸馏
- 👤 Gongbo Zhang, Wen Wang, Ye Tian, Li Yuan | 北京大学、浙江大学
- 📍 arXiv | cs.CL, cs.AI, cs.LG
- 🔬 创新点深度解析：
  1. **问题背景**：dLLM 参数量大，推理成本高...
  2. **现有方法的不足**：现有蒸馏仅在同一架构内...
  3. **核心方法**：TIDE 框架包含三个模块...
  4. **关键创新点**：首次解决跨架构蒸馏问题...
  5. **实验结果**：在多个基准上优于 baseline...

### 📊 今日趋势
一句话总结...
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install pymupdf
```

### 2. 下载脚本

```bash
git clone https://github.com/Yiwen20/ai-daily-digest.git
cd ai-daily-digest
```

### 3. 手动运行

```bash
python3 scripts/fetch_ai_news.py
```

### 4. 定时任务（可选）

#### 方式一：Hermes Agent（推荐）

```python
# 在 Hermes Agent 中创建定时任务
cronjob(
    action="create",
    name="AI Daily Digest",
    schedule="0 9 * * 1-5",  # 工作日 9:00
    deliver="weixin"  # 推送到微信
)
```

#### 方式二：系统 Cron

```bash
# 编辑 crontab
crontab -e

# 添加（工作日 9:00 运行）
0 9 * * 1-5 cd /path/to/ai-daily-digest && python3 scripts/fetch_ai_news.py >> /var/log/ai-daily.log 2>&1
```

## 📁 项目结构

```
ai-daily-digest/
├── README.md              # 项目介绍
├── SKILL.md               # Hermes Agent Skill 定义
├── LICENSE                # MIT 协议
├── scripts/
│   └── fetch_ai_news.py   # 核心采集脚本
├── config/
│   └── sources.yaml       # 数据源配置
└── examples/
    └── sample_output.md   # 日报示例
```

## ⚙️ 配置

编辑 `config/sources.yaml` 可以自定义：

```yaml
arxiv:
  max_papers: 5           # 最多采集几篇论文
  extract_pdf: true       # 是否下载 PDF 提取全文
  queries:                # 搜索关键词（支持 LLM 相关）
    - name: LLM-Core
      query: "ti:language+model+OR+ti:LLM+OR+ti:GPT"
```

## 📊 数据源详情

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

### 学术来源
| 来源 | 特点 |
|------|------|
| arXiv | 最新预印本，支持 PDF 全文提取 |
| OpenAlex | 已发表论文，含作者单位和引用数 |
| DBLP | CS 会议论文，含会议简称 |

## 🤖 Hermes Agent 集成

本项目是一个 [Hermes Agent](https://github.com/hermes-agent) Skill。

### 什么是 Hermes Agent？

Hermes Agent 是一个开源的 AI 代理框架，支持：
- 多平台消息推送（微信、Telegram、Discord）
- 定时任务调度
- 技能（Skill）系统
- 工具调用和代码执行

### 如何使用

1. 安装 Hermes Agent
2. 将 `SKILL.md` 放入 skills 目录
3. 在 Agent 中创建定时任务
4. 自动推送日报到微信/Telegram

## 📝 更新日志

### v1.0.0 (2026-04-30)
- ✨ 初始版本
- 🗞️ 支持 11 个数据源
- 📄 支持 arXiv PDF 全文提取
- 🔬 支持创新点深度解析
- 📍 支持作者单位和会议信息提取

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
