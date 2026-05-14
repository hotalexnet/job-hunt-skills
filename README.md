# job-hunt-skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/hotalexnet/job-hunt-skills?style=social)](https://github.com/hotalexnet/job-hunt-skills/stargazers)
[![Last commit](https://img.shields.io/github/last-commit/hotalexnet/job-hunt-skills)](https://github.com/hotalexnet/job-hunt-skills/commits/main)
[![Runtime: Python 3](https://img.shields.io/badge/runtime-python3-blue.svg)](https://www.python.org/)
**English** | [**中文**](./README.zh-CN.md)

Hermes Agent skills for automated job hunting on [BOSS直聘](https://www.zhipin.com) (Boss Zhipin) — China's largest tech recruitment platform. Scrape recommended jobs via API, score match quality, generate personalized greetings, and push results to Feishu/Telegram daily.

## What It Does

- **boss-greeting** — Personalized greeting generator. Produces 3 tailored versions (experience-driven / achievement-showcase / straight-shooter) for each job, 80-120 Chinese characters, with JD keyword matching.
- **boss-scraper** — API-based job scraper with match scoring (1-10), batch greeting generation, and daily push to messaging platforms.

**Why this exists:** Instead of scrolling through hundreds of irrelevant listings, let the agent filter, score, and draft your outreach — you just copy and send.

## Features

- Match scoring (1-10) based on your profile vs JD — only shows jobs worth applying to
- 3 greeting styles per job, 80-120 Chinese characters, with JD keywords baked in
- Cookie-based API auth — no browser automation, no CAPTCHA headaches
- Built-in anti-detection (rate limiting, request caps, fixed User-Agent)
- Daily cron scan with results pushed to Feishu or Telegram
- Fully customizable scoring weights, greeting templates, and user profile

## Install

### Prerequisites

- [Hermes Agent](https://github.com/openclaw/openclaw) deployed and connected to Feishu or Telegram
- Firefox browser (for cookie export)

### Option 1: Download SKILL.md directly

```bash
# Local deployment
mkdir -p ~/.hermes/skills/career/boss-greeting
mkdir -p ~/.hermes/skills/career/boss-scraper

curl -o ~/.hermes/skills/career/boss-greeting/SKILL.md \
  https://raw.githubusercontent.com/hotalexnet/job-hunt-skills/main/skills/career/boss-greeting/SKILL.md

curl -o ~/.hermes/skills/career/boss-scraper/SKILL.md \
  https://raw.githubusercontent.com/hotalexnet/job-hunt-skills/main/skills/career/boss-scraper/SKILL.md
```

```bash
# Docker deployment (volume mount: /root/.hermes → /opt/data)
doas mkdir -p /root/.hermes/skills/career/boss-greeting
doas mkdir -p /root/.hermes/skills/career/boss-scraper

doas curl -o /root/.hermes/skills/career/boss-greeting/SKILL.md \
  https://raw.githubusercontent.com/hotalexnet/job-hunt-skills/main/skills/career/boss-greeting/SKILL.md

doas curl -o /root/.hermes/skills/career/boss-scraper/SKILL.md \
  https://raw.githubusercontent.com/hotalexnet/job-hunt-skills/main/skills/career/boss-scraper/SKILL.md

# Restart Hermes to load new skills
doas docker restart hermes hermes-dashboard
```

After installing, send `/reload-skills` in Feishu to refresh.

### Option 2: Clone the repo

```bash
git clone https://github.com/hotalexnet/job-hunt-skills.git
cp -r job-hunt-skills/skills/career/ ~/.hermes/skills/career/
```

## Setup

### 1. Configure your profile

Tell Hermes about your background in a conversation:

> "My profile: X years tech experience, focused on AI Agent, tech stack includes LangChain/RAG/vector search. Looking for: AI Agent engineer roles, remote preferred."

Hermes remembers this for scoring and greeting generation.

### 2. Export BOSS直聘 cookies

Login to [zhipin.com](https://www.zhipin.com) in Firefox, then:

```bash
# Export cookies
python3 scripts/boss-cookie.py export

# Copy to Hermes data directory
# Docker:
doas cp ~/.hermes/boss-cookies.json /root/.hermes/boss-cookies.json

# Local:
cp ~/.hermes/boss-cookies.json ~/.hermes/boss-cookies.json
```

### 3. Test

Say this to Hermes in Feishu/Telegram:

```
帮我看看BOSS直聘有什么新职位
```

### 4. Set up daily cron (optional)

```
hermes cron add "0 9 * * *" "帮我看看BOSS直聘上今天有什么新职位" --platform feishu
```

## Usage

| Trigger | Action |
|---------|--------|
| "帮我看看新职位" / "扫描BOSS直聘" | Scrape → score → generate greetings → push |
| Paste a JD | Generate 3 greeting versions for that specific job |
| Cron (daily 9:00) | Auto scan and push results |

**Sample push output:**

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

## How It Works

```
BOSS直聘 Recommend API (read-only, no CAPTCHA)
    ↓
Job list → Match scoring (1-10)
    ↓
Jobs scoring ≥6 → Personalized greeting generation (80-120 characters)
    ↓
Push to Feishu / Telegram
    ↓
User copies greeting → Sends manually in BOSS直聘 app
```

**Why manual sending?** BOSS直聘 has aggressive anti-bot detection for write operations (dynamic tokens + icon-selection CAPTCHA). Auto-sending risks account bans. This tool focuses on screening + drafting; the actual sending is done by you.

## Cookie Refresh

Cookies expire every 7-30 days. When the API returns errors:

1. Re-login to zhipin.com in Firefox
2. Run `python3 scripts/boss-cookie.py export`
3. Copy to Hermes data directory

## Match Scoring

| Factor | Weight | Rules |
|--------|--------|-------|
| Direction | 40% | AI Agent / LLM / RAG / LangChain / Automation |
| Tech stack | 30% | Python/Linux/Docker/vector search/Claude/GPT/full-stack, +1 each, max +3 |
| Location | 15% | Remote +2, Tier-1 city +1 |
| Salary | 10% | ≥40K +1, 25-40K 0, <25K -1 |
| Role level | 5% | Co-founder/CTO/VP +1 |

Weights and keywords are fully customizable in the SKILL.md files.

## Customization

- **Scoring rules**: Edit the scoring table in `boss-scraper/SKILL.md` Step 3
- **Greeting styles**: Edit templates and principles in `boss-greeting/SKILL.md` Step 3
- **User profile**: Update directly in Hermes conversation — it remembers
- **Push schedule**: Modify the cron expression

## Project Structure

```
job-hunt-skills/
├── README.md                    # This file (English)
├── README.zh-CN.md              # 中文文档
├── LICENSE
├── scripts/
│   └── boss-cookie.py           # Cookie export tool
└── skills/
    └── career/
        ├── boss-greeting/
        │   └── SKILL.md         # Greeting generation skill
        └── boss-scraper/
            └── SKILL.md         # Job scraping + scoring + push skill
```

## License

[MIT License](LICENSE)

## Acknowledgments

- [Hermes Agent](https://github.com/openclaw/openclaw) — AI Agent framework
- [BOSS直聘](https://www.zhipin.com) — Job data source

---

⚠️ **Disclaimer**: This project is for educational purposes only. Please comply with BOSS直聘's Terms of Service and applicable laws. The developer assumes no liability for any issues arising from the use of this project.
