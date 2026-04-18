# test-orchestrator-bot

Telegram bot that triggers tests in GitHub Actions and reports the result back to the chat.

Built to avoid opening GitHub UI every time you need to run tests or check results.

---

## How it works

```
Telegram → GitHub REST API → workflow_dispatch
                                    ↓
                            GitHub Actions CI
                                    ↓
                            pytest (UI/API/E2E/Mobile)
                                    ↓
                            Allure Report → GitHub Pages
                                    ↓
                         status reported back to Telegram
```

The bot doesn't run tests itself — it only calls the GitHub API.
All execution logic stays in CI.

---

## Commands

| Command | What it does |
|---|---|
| `/start` | Main menu with buttons |
| `/run_all` | Run all tests |
| `/run_ui` | UI tests only |
| `/run_api` | API tests only |
| `/run_e2e` | E2E tests only |
| `/run_mobile` | Mobile tests only |
| `/status` | Last run status + per-job breakdown |

After triggering, a **Retry** button appears to re-dispatch the same suite.

---

## Structure

```
bot/
├── bot.py              # entry point, polling
├── config.py           # env vars via dotenv
├── handlers/
│   ├── commands.py     # /start, /run_*, /status
│   └── callbacks.py    # inline buttons, retry
├── keyboards/
│   └── inline.py       # main menu, after_run, status
└── services/
    └── github.py       # dispatch, get_run, get_jobs
```

---

## Setup

```bash
cp .env.example .env
# fill in the values

pip install -r requirements.txt
python bot.py

# or with Docker
docker-compose up -d
```

## .env

```env
BOT_TOKEN=        # from @BotFather
GITHUB_TOKEN=     # Personal Access Token
GITHUB_REPO=      # the test repository
WORKFLOW_ID=      # tests.yml
GITHUB_BRANCH=    # main
```

---

## Design decisions

**Polling over webhook** — no need for a public server. For a pet project polling is fine, latency difference doesn't matter here.

**Bot and tests in separate repositories** — the bot controls CI but knows nothing about the tests. Switching the test repo is just changing `GITHUB_REPO` in `.env`.

**Per-job status via jobs API** — `/status` shows not just the overall `success/failure` of a run, but the status of each job individually. You can see exactly where it failed.

**No database** — the last `run_id` is stored in process memory. Lost on restart. Good enough for current needs.

---

## Limitations

- run history is not persisted between bot restarts
- no authorization — any user can trigger tests
- no request queue — two simultaneous dispatches create two runs

---
## Example
### Telegram bot
<img width="329" height="398" alt="IMG_9383" src="https://github.com/user-attachments/assets/24712db3-db7d-413d-848a-5f1c624533be" />
