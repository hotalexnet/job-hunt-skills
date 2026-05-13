# hermes-boss-skills

Hermes Agent skills for BOSS直聘（Boss Zhipin）job hunting automation.

## What it does

- **boss-greeting**: Generate personalized greetings for BOSS直聘 job applications based on your resume and the job description
- **boss-scraper**: Scrape recommended jobs via API, score match quality, batch generate greetings, and push results to Feishu/Telegram daily

## Features

- 🎯 Auto match scoring (1-10) based on your profile vs JD
- ✍️ Personalized greeting generation (3 versions: experience, achievement, co-founder)
- 📋 Daily cron scan pushed to messaging platforms
- 🔒 Cookie-based API auth — no browser automation, no CAPTCHA issues
- 🛡️ Anti-detection built in (rate limits, request caps)

## Install

```bash
# Add as a Hermes skill tap
hermes skills tap add hotalexnet/hermes-boss-skills

# Install individual skills
hermes skills install hotalexnet/hermes-boss-skills/skills/career/boss-greeting
hermes skills install hotalexnet/hermes-boss-skills/skills/career/boss-scraper
```

Or install directly:
```bash
hermes skills install https://github.com/hotalexnet/hermes-boss-skills/raw/main/skills/career/boss-greeting/SKILL.md --name boss-greeting
hermes skills install https://github.com/hotalexnet/hermes-boss-skills/raw/main/skills/career/boss-scraper/SKILL.md --name boss-scraper
```

## Setup

### 1. Configure your profile

After installation, tell Hermes about yourself in a conversation:
> "My profile: 26 years tech experience, AI Agent direction, looking for AI Agent engineer or technical co-founder roles, remote preferred. Tech stack: Linux/BSD, Claude Code, Codex, LangChain, RAG."

Hermes will remember this for greeting generation.

### 2. Export BOSS直聘 cookies

Login to zhipin.com in Firefox, then run:

```bash
python3 scripts/boss-cookie.py export
```

Copy cookies to Hermes data dir:

```bash
# If Hermes runs locally:
cp ~/.hermes/boss-cookies.json ~/.hermes/boss-cookies.json

# If Hermes runs in Docker with volume mount:
doas cp ~/.hermes/boss-cookies.json /root/.hermes/boss-cookies.json
```

### 3. Test

```
帮我看看BOSS直聘有什么新职位
```

### 4. (Optional) Set up daily cron

```
hermes cron add "0 9 * * *" "帮我看看BOSS直聘上今天有什么新职位" --platform feishu
```

## Usage

| Trigger | Action |
|---------|--------|
| "帮我看看新职位" / "扫描BOSS直聘" | Scrape + score + generate greetings |
| Paste a JD | Generate greeting for that specific job |
| Cron (daily 9:00) | Auto scan and push to messaging platform |

## Architecture

```
BOSS直聘 API (read-only, no CAPTCHA)
    ↓
Job list → Match scoring → Greeting generation
    ↓
Push to Feishu / Telegram
    ↓
User copies greeting → Sends manually in BOSS直聘 app
```

Write operations (sending greetings) are intentionally manual to avoid account bans. The value is in automated screening + personalized greeting generation.

## Cookie Refresh

Cookies expire every 7-30 days. When API returns errors:

1. Login to zhipin.com in Firefox
2. Run `python3 scripts/boss-cookie.py export`
3. Copy to Hermes data directory

## License

MIT
