# QA Bot

Telegram-бот для запуска тестов через GitHub Actions.

## Запуск

```bash
cp .env.example .env  # заполни значения
pip install -r requirements.txt
python bot.py
```

## .env

```env
BOT_TOKEN=     # @BotFather
GITHUB_TOKEN=  # github.com/settings/tokens (scope: repo)
REPO=          # owner/repo
WORKFLOW_ID=   # tests.yml
```

## Команды

`/start` `/run_all` `/run_ui` `/run_api` `/run_e2e` `/status`