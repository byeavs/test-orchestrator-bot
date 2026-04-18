# test-orchestrator-bot

Telegram-бот, который запускает тесты в GitHub Actions и возвращает статус прямо в чат.

Сделан чтобы не лезть в GitHub UI каждый раз когда нужно прогнать тесты или проверить результат.

---

## Как это работает

```
Telegram → GitHub REST API → workflow_dispatch
                                    ↓
                            GitHub Actions CI
                                    ↓
                            pytest (UI/API/E2E/Mobile)
                                    ↓
                            Allure Report → GitHub Pages
                                    ↓
                         статус обратно в Telegram
```

Бот не запускает тесты сам — он только дёргает GitHub API.
Вся логика выполнения остаётся в CI.

---

## Команды

| Команда | Что делает |
|---|---|
| `/start` | Главное меню с кнопками |
| `/run_all` | Запустить все тесты |
| `/run_ui` | Только UI |
| `/run_api` | Только API |
| `/run_e2e` | Только E2E |
| `/run_mobile` | Только Mobile |
| `/status` | Статус последнего запуска + статус каждого job |

После запуска появляется кнопка **Retry** — повторный dispatch того же suite.

---

## Структура

```
bot/
├── bot.py              # точка входа, polling
├── config.py           # env vars через dotenv
├── handlers/
│   ├── commands.py     # /start, /run_*, /status
│   └── callbacks.py    # inline кнопки, retry
├── keyboards/
│   └── inline.py       # main menu, after_run, status
└── services/
    └── github.py       # dispatch, get_run, get_jobs
```

---

## Запуск

```bash
cp .env.example .env
# заполни значения

pip install -r requirements.txt
python bot.py

# или через Docker
docker-compose up -d
```

## .env

```env
BOT_TOKEN=        # @BotFather
GITHUB_TOKEN=     # Personal Access Token
GITHUB_REPO=      # репо с тестами
WORKFLOW_ID=      # tests.yml
GITHUB_BRANCH=    # main
```

---

## Design decisions

**Polling вместо webhook** — не нужен публичный сервер. Для pet-проекта polling достаточен, разница в latency несущественна.

**Бот и тесты в разных репозиториях** — бот управляет CI, но не знает про тесты. Можно поменять тестовый репо просто изменив `GITHUB_REPO` в `.env`.

**Статус через jobs API** — `/status` показывает не просто `success/failure` всего run, а статус каждого job отдельно. Сразу видно где упало.

**Нет БД** — последний `run_id` хранится в памяти процесса. При перезапуске бота история теряется. Для текущих задач этого достаточно.

---

## Ограничения

- история запусков не сохраняется между перезапусками бота
- нет авторизации — любой пользователь может запустить тесты
- нет очереди запросов — два одновременных dispatch создадут два run

---

## Что можно улучшить

- добавить whitelist chat_id — ограничить доступ к боту
- хранить историю run_id в SQLite или Redis
- присылать уведомление автоматически когда CI завершился (polling run до completion)
- добавить выбор ветки перед запуском
