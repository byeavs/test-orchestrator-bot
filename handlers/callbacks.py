import asyncio
import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery

from keyboards.inline import (
    after_run_kb,
    back_to_menu_kb,
    main_menu_kb,
    status_kb,
)
from services.github import GitHubService

logger = logging.getLogger(__name__)
router = Router()

_SUITE_LABELS = {
    "all": "ALL",
    "ui": "UI",
    "api": "API",
    "e2e": "E2E",
    "interation": "INTEGRATION"
}


def setup_callbacks_router(github: GitHubService) -> Router:

    # ------------------------------------------------------------------ #
    #  run:<suite>                                                       #
    # ------------------------------------------------------------------ #
    @router.callback_query(F.data.startswith("run:"))
    async def cb_run(call: CallbackQuery):
        suite = call.data.split(":")[1]
        label = _SUITE_LABELS.get(suite, suite.upper())

        await call.message.edit_text(f"⏳ Triggering <b>{label}</b> tests…")
        await call.answer()

        ok = await github.dispatch_workflow(inputs={"test_suite": suite})

        if ok:
            run = await github.get_latest_run()
            url = run.html_url if run else "https://github.com"

            await call.message.edit_text(
                f"🚀 <b>{label}</b> pipeline triggered!\n\n"
                "I'll notify you when it's done.",
                reply_markup=after_run_kb(url),
            )

            if run:
                bot = call.message.bot
                chat_id = call.message.chat.id
                run_id = run.run_id

                async def notify(summary: str):
                    try:
                        await bot.send_message(chat_id, summary)
                    except Exception as exc:
                        logger.error("notify failed: %s", exc)

                asyncio.create_task(
                    github.poll_until_complete(run_id=run_id, on_complete=notify)
                )
            # ──────────────────────────────────────────────────────────

        else:
            await call.message.edit_text(
                "❌ Failed to trigger workflow.\n"
                "Check your <code>GITHUB_TOKEN</code> and repo settings.",
                reply_markup=back_to_menu_kb(),
            )

    # ------------------------------------------------------------------ #
    #  status                                                            #
    # ------------------------------------------------------------------ #
    @router.callback_query(F.data == "status")
    async def cb_status(call: CallbackQuery):
        await call.message.edit_text("🔄 Fetching status…")
        await call.answer()

        text, url, allure_url = await github.get_status_text()
        if url:
            await call.message.edit_text(text, reply_markup=status_kb(url, allure_url))
        else:
            await call.message.edit_text(text, reply_markup=back_to_menu_kb())

    # ------------------------------------------------------------------ #
    #  retry                                                             #
    # ------------------------------------------------------------------ #
    @router.callback_query(F.data == "retry")
    async def cb_retry(call: CallbackQuery):
        await call.message.edit_text("🔁 Retrying last workflow…")
        await call.answer()

        ok = await github.dispatch_workflow()
        if ok:
            run = await github.get_latest_run()
            url = run.html_url if run else "https://github.com"

            await call.message.edit_text(
                "🔁 Workflow re-triggered!\n\n"
                "I'll notify you when it's done.",
                reply_markup=after_run_kb(url),
            )

            if run:
                bot = call.message.bot
                chat_id = call.message.chat.id
                run_id = run.run_id

                async def notify_retry(summary: str):
                    try:
                        await bot.send_message(chat_id, summary)
                    except Exception as exc:
                        logger.error("notify_retry failed: %s", exc)

                asyncio.create_task(
                    github.poll_until_complete(run_id=run_id, on_complete=notify_retry)
                )
            # ──────────────────────────────────────────────────────────

        else:
            await call.message.edit_text(
                "❌ Retry failed. Check token/repo settings.",
                reply_markup=back_to_menu_kb(),
            )

    # ------------------------------------------------------------------ #
    #  menu                                                              #
    # ------------------------------------------------------------------ #
    @router.callback_query(F.data == "menu")
    async def cb_menu(call: CallbackQuery):
        await call.answer()
        await call.message.edit_text(
            "👋 <b>QA Automation Bot</b>\n\n"
            "Test pipeline.",
            reply_markup=main_menu_kb(),
        )

    return router