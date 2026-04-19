# test-orchestrator-bot

Telegram-бот, который запускает тесты в GitHub Actions и возвращает результат прямо в чат.

Сделан чтобы не лезть в GitHub UI каждый раз когда нужно прогнать тесты или проверить статус.

---

## Как это работает

```
Telegram → GitHub REST API → workflow_dispatch
                                    ↓
                            GitHub Actions CI
                                    ↓
                            pytest (UI/API/E2E/Mobile/Integration)
                                    ↓
                            Allure Report → GitHub Pages
                                    ↓
                    авто-уведомление с результатом в Telegram
```

Бот не запускает тесты сам — он только дёргает GitHub API.
После запуска бот сам следит за прогрессом и пишет результат когда CI завершился.

---

## Команды

| Команда | Что делает |
|---|---|
| `/start` | Главное меню с кнопками |
| `/run_all` | Запустить все тесты |
| `/run_ui` | Только UI |
| `/run_api` | Только API |
| `/run_e2e` | Только E2E |
| `/status` | Статус последнего запуска + per-job breakdown |

После запуска появляется кнопка **Retry** — повторный dispatch того же suite.

---

## Авто-уведомление

После запуска бот сам следит за CI и присылает результат без `/status`:

```
✅ Run #42 — success

✅ API Tests:         success
✅ UI Tests:          success
❌ E2E Tests:         failure
✅ Mobile Tests:      success
✅ Integration Tests: success

🔗 GitHub Actions  📊 Allure Report
```

Реализовано через `asyncio.create_task` — background polling каждые 30 сек, без блокировки бота.

---

## Структура

```
├── bot.py              # точка входа, polling
├── config.py           # env vars через dotenv
├── handlers/
│   ├── commands.py     # /start, /run_*, /status + auto-notify
│   └── callbacks.py    # inline кнопки, retry + auto-notify
├── keyboards/
│   └── inline.py       # main_menu, after_run, status клавиатуры
└── services/
    └── github.py       # dispatch, poll_until_complete, get_jobs, format_summary
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

**Polling вместо webhook** — не нужен публичный сервер. Для pet-проекта разница в latency несущественна.

**Бот и тесты в разных репозиториях** — бот управляет CI, но не знает про тесты. Смена тестового репо — это просто `GITHUB_REPO` в `.env`.

**Per-job статус** — `/status` показывает не просто `success/failure` run, а статус каждого job. Сразу видно где упало.

**Background polling через asyncio.create_task** — бот не блокируется пока ждёт CI. Можно запускать несколько suite параллельно, каждый придёт отдельным уведомлением.

**Нет БД** — `run_id` хранится в памяти. При перезапуске теряется. Для текущих задач достаточно.

---

## Ограничения

- история запусков не сохраняется между перезапусками
- нет авторизации — любой пользователь может запустить тесты
- два одновременных dispatch создадут два run

---

## Скриншот

<img width="329" height="398" alt="IMG_9383" src="https://github.com/user-attachments/assets/24712db3-db7d-413d-848a-5f1c624533be" />