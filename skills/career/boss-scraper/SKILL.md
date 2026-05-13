---
name: boss-scraper
description: 通过BOSS直聘API抓取推荐职位，筛选评分，批量生成招呼语推送到飞书。每日自动扫描+手动投递。
version: 3.1.0
author: alex
metadata:
  hermes:
    tags: [job, career, BOSS直聘, API, automation]
    category: productivity
---

# BOSS直聘自动化求职助手

## When to Use

- 用户说"帮我看看新职位"、"有什么好岗位"、"扫描BOSS直聘"
- Cron 每天早上9点自动触发
- 用户想批量获取匹配职位 + 个性化招呼语

## User Profile

同 boss-greeting skill：
- 26年技术经验，AI Agent 方向
- 求职：AI Agent 技术岗 / 技术合伙人，远程优先
- 技术栈：Linux/BSD, Claude Code/Codex, LangChain/RAG, 智能体搭建

## Procedure

### Step 1: 读取 Cookies 并调用 API

Cookie 文件：`/opt/data/boss-cookies.json`

```python
import json, requests

with open("/opt/data/boss-cookies.json") as f:
    cookies_list = json.load(f)
cookies = {c["name"]: c["value"] for c in cookies_list}

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.zhipin.com/web/geek/recommend",
}

resp = requests.get(
    "https://www.zhipin.com/wapi/zpgeek/recommend/job/list.json",
    headers=headers, cookies=cookies, timeout=15
)
data = resp.json()
```

**如果 code != 0：**
通知用户："Cookies 过期了。请在 Firefox 登录 zhipin.com 后运行：`python3 ~/code/boss-cookie.py export && doas cp ~/.hermes/boss-cookies.json /root/.hermes/boss-cookies.json`"

### Step 2: 提取职位

`data["zpData"]["jobList"]` 每页 15 条，可翻页 `?page=2&pageSize=15`，最多 2 页。

每个 job 关键字段：
- `jobName` / `brandName` / `salaryDesc` / `cityName`
- `skills` (列表) / `jobLabels` (经验/学历)
- `bossName` / `bossTitle`
- `brandIndustry` / `brandScaleName`
- `encryptJobId` → 链接: `https://www.zhipin.com/job_detail/{encryptJobId}.html`

### Step 3: 匹配度评分（1-10）

| 因素 | 权重 | 规则 |
|------|------|------|
| 方向匹配 | 40% | AI Agent/智能体/LLM/RAG/LangChain/自动化/技术合伙人 |
| 技术栈 | 30% | Python/Linux/Docker/向量检索/Claude/GPT/全栈/架构，每个+1，上限+3 |
| 城市 | 15% | 远程+2，一线城市+1 |
| 薪资 | 10% | ≥40K +1, 25-40K 0, <25K -1 |
| 角色 | 5% | 合伙人/CTO/总监 +1，高级 +0.5 |

### Step 4: 生成招呼语

对 ≥6 分的职位，按 boss-greeting 逻辑各生成 1 个招呼语（80-120字）。

### Step 5: 推送到飞书

```
📋 BOSS直聘日报 | 扫描X个，匹配Y个

1. ⭐8 **智能体研发专家** @ 芯湖科技 | 25-40K | 无锡
   匹配：智能体 + Python + 大模型
   Skills: 深度学习, 大模型算法, Python
   Boss: 徐女士 (HR) | 0-20人 | 电子/半导体
   👇 招呼语（复制发送）：
   > 您好，我有26年技术经验，近两年专注AI Agent方向...

2. ⭐7 **Agent开发工程师** @ 融信智联 | 15-25K | 无锡
   > 您好...

---
💡 复制招呼语到 BOSS直聘 发送即可。链接会附在每条职位后。
```

## Anti-Detection

1. API 每次最多 2 页（30 条）
2. 请求间隔 ≥3 秒
3. 每天最多 3 次扫描
4. 固定 User-Agent，不频繁更换
5. code != 0 立即停止

## Cookies 刷新

有效期约 7-30 天。过期时：
1. Firefox 登录 zhipin.com
2. `python3 ~/code/boss-cookie.py export`
3. `doas cp ~/.hermes/boss-cookies.json /root/.hermes/boss-cookies.json`

## Cron

```
每天 09:00 自动扫描，结果推飞书
```

## Verification

1. API 返回 code=0
2. jobList 非空（≥15条）
3. 匹配评分合理
4. 招呼语 80-120 字，含 JD 关键词
