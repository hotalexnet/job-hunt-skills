# job-hunt-skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[**English**](./README.md) | **中文**

Hermes Agent 技能包 —— BOSS直聘自动化求职助手。通过 API 抓取推荐职位，智能匹配评分，生成个性化招呼语，每日推送到飞书/Telegram。

## 功能

- **boss-greeting** — 个性化招呼语生成器，根据 JD 定制 3 版招呼语（经验直击 / 成果展示 / 实战亮剑）
- **boss-scraper** — API 职位抓取 + 匹配评分 + 批量招呼语生成 + 飞书/Telegram 推送

**亮点：**
- 匹配度评分（1-10），只推送值得投的职位
- 3 种风格招呼语，80-120 字，含 JD 关键词复现
- Cookie 认证，不碰浏览器，绕过验证码
- 内置反爬策略（限频、限次、固定 UA）
- 每日定时推送，复制招呼语手动发送

## 安装

### 前提

- 已部署 [Hermes Agent](https://github.com/openclaw/openclaw) 并连接飞书或 Telegram
- Firefox 浏览器（用于导出 cookies）

### 方式一：直接下载 SKILL.md

```bash
# 下载到 Hermes skills 目录（本地部署）
curl -o ~/.hermes/skills/career/boss-greeting/SKILL.md \
  https://raw.githubusercontent.com/hotalexnet/job-hunt-skills/main/skills/career/boss-greeting/SKILL.md

curl -o ~/.hermes/skills/career/boss-scraper/SKILL.md \
  https://raw.githubusercontent.com/hotalexnet/job-hunt-skills/main/skills/career/boss-scraper/SKILL.md
```

```bash
# Docker 部署（假设挂载 /root/.hermes → /opt/data）
doas mkdir -p /root/.hermes/skills/career/boss-greeting
doas mkdir -p /root/.hermes/skills/career/boss-scraper

doas curl -o /root/.hermes/skills/career/boss-greeting/SKILL.md \
  https://raw.githubusercontent.com/hotalexnet/job-hunt-skills/main/skills/career/boss-greeting/SKILL.md

doas curl -o /root/.hermes/skills/career/boss-scraper/SKILL.md \
  https://raw.githubusercontent.com/hotalexnet/job-hunt-skills/main/skills/career/boss-scraper/SKILL.md

# 重启 Hermes 加载技能
doas docker restart hermes hermes-dashboard
```

安装后在飞书发送 `/reload-skills` 刷新。

### 方式二：克隆仓库

```bash
git clone https://github.com/hotalexnet/job-hunt-skills.git
# 将 skills/ 目录复制到 Hermes skills 路径
cp -r job-hunt-skills/skills/career/ ~/.hermes/skills/career/
```

## 配置

### 1. 设置个人画像

在 Hermes 对话中告诉它你的背景，例如：

> 我的背景：X年技术经验，专注AI Agent方向，技术栈包括 LangChain/RAG/向量检索。求职方向：AI Agent 工程师，远程优先。

Hermes 会记住这些信息用于招呼语生成和匹配评分。

### 2. 导出 BOSS直聘 Cookies

先在 Firefox 中登录 [zhipin.com](https://www.zhipin.com)，然后：

```bash
# 导出 cookies
python3 scripts/boss-cookie.py export

# 复制到 Hermes 数据目录
# Docker 部署：
doas cp ~/.hermes/boss-cookies.json /root/.hermes/boss-cookies.json

# 本地部署：
cp ~/.hermes/boss-cookies.json ~/.hermes/boss-cookies.json
```

### 3. 测试

在飞书/Telegram 对 Hermes 说：

```
帮我看看BOSS直聘有什么新职位
```

### 4. 设置每日定时推送（可选）

```
hermes cron add "0 9 * * *" "帮我看看BOSS直聘上今天有什么新职位" --platform feishu
```

## 使用

| 触发方式 | 动作 |
|---------|------|
| "帮我看看新职位" / "扫描BOSS直聘" | 抓取推荐职位 → 评分 → 生成招呼语 → 推送 |
| 粘贴一段 JD | 针对该职位生成 3 版招呼语 |
| 每日 09:00 定时任务 | 自动扫描并推送结果到飞书 |

**推送示例：**

```
📋 BOSS直聘日报 | 扫描30个，匹配5个

1. ⭐8 智能体研发专家 @ 芯湖科技 | 25-40K | 无锡
   匹配：智能体 + Python + 大模型
   Boss: 徐女士 (HR) | 0-20人
   👇 招呼语（复制发送）：
   > 您好，26年Linux/BSD资深工程师，近一年All in AI Agent...

2. ⭐7 Agent开发工程师 @ 融信智联 | 15-25K | 无锡
   > ...
```

## 工作原理

```
BOSS直聘推荐 API (只读，无验证码)
    ↓
职位列表 → 匹配度评分 (1-10)
    ↓
≥6分的职位 → 生成个性化招呼语 (80-120字)
    ↓
推送到飞书 / Telegram
    ↓
用户复制招呼语 → 在 BOSS直聘 手动发送
```

**为什么不自动发送？** BOSS直聘对自动发送有严格的反机器人检测（动态令牌 + 图标验证码），自动发送有封号风险。本项目定位是「筛选+生成」，发送环节由用户手动完成。

## Cookie 刷新

Cookies 有效期约 7-30 天。过期时 API 会报错，按以下步骤刷新：

1. 在 Firefox 中重新登录 zhipin.com
2. 运行 `python3 scripts/boss-cookie.py export`
3. 复制到 Hermes 数据目录

## 匹配评分规则

| 因素 | 权重 | 规则 |
|------|------|------|
| 方向匹配 | 40% | AI Agent/智能体/LLM/RAG/LangChain/自动化 |
| 技术栈 | 30% | Python/Linux/Docker/向量检索/Claude/GPT/全栈，每个+1，上限+3 |
| 城市 | 15% | 远程+2，一线城市+1 |
| 薪资 | 10% | ≥40K +1, 25-40K 0, <25K -1 |
| 角色 | 5% | 合伙人/CTO/总监 +1 |

评分可在 SKILL.md 中自定义调整权重和关键词。

## 自定义

- **匹配评分**：编辑 `boss-scraper/SKILL.md` 中 Step 3 的评分表
- **招呼语风格**：编辑 `boss-greeting/SKILL.md` 中 Step 3 的模板和原则
- **用户画像**：在 Hermes 对话中直接更新，它会记住
- **推送时间**：修改 cron 表达式

## 项目结构

```
job-hunt-skills/
├── README.md                    # English documentation
├── README.zh-CN.md              # 中文文档（本文件）
├── LICENSE
├── scripts/
│   └── boss-cookie.py          # Cookie 导出工具
└── skills/
    └── career/
        ├── boss-greeting/
        │   └── SKILL.md        # 招呼语生成技能
        └── boss-scraper/
            └── SKILL.md        # 职位抓取+评分+推送技能
```

## 许可证

[MIT License](LICENSE)

## 致谢

- [Hermes Agent](https://github.com/openclaw/openclaw) — AI Agent 框架
- [BOSS直聘](https://www.zhipin.com) — 职位数据来源

---

⚠️ **免责声明**：本项目仅供学习交流使用。使用时请遵守 BOSS直聘的用户协议和相关法律法规。因使用本项目导致的任何问题，开发者不承担责任。
