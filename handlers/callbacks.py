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
    "ui":  "UI",
    "api": "API",
    "e2e": "E2E",
}


def setup_callbacks_router(github: GitHubService) -> Router:

    @router.callback_query(F.data.startswith("run:"))
    async def cb_run(call: CallbackQuery):
        suite = call.data.split(":")[1]
        label = _SUITE_LABELS.get(suite, suite.upper())

        await call.message.edit_text(f"⏳ Triggering <b>{label}</b> tests…")
        await call.answer()

        inputs = {} if suite == "all" else {"suite": suite}
        ok = await github.dispatch_workflow(inputs=inputs)

        if ok:
            run = await github.get_latest_run()
            url = run.html_url if run else "https://github.com"
            await call.message.edit_text(
                f"🚀 <b>{label}</b> pipeline triggered!\n\n"
                "GitHub Actions is now processing your request.",
                reply_markup=after_run_kb(url),
            )
        else:
            await call.message.edit_text(
                "❌ Failed to trigger workflow.\n"
                "Check your <code>GITHUB_TOKEN</code> and repo settings.",
                reply_markup=back_to_menu_kb(),
            )

    @router.callback_query(F.data == "status")
    async def cb_status(call: CallbackQuery):
        await call.message.edit_text("🔄 Fetching status…")
        await call.answer()

        text, url = await github.get_status_text()
        if url:
            await call.message.edit_text(text, reply_markup=status_kb(url))
        else:
            await call.message.edit_text(text, reply_markup=back_to_menu_kb())

    @router.callback_query(F.data == "retry")
    async def cb_retry(call: CallbackQuery):
        await call.message.edit_text("🔁 Retrying last workflow…")
        await call.answer()

        ok = await github.dispatch_workflow()
        if ok:
            run = await github.get_latest_run()
            url = run.html_url if run else "https://github.com"
            await call.message.edit_text(
                "🔁 Workflow re-triggered successfully!",
                reply_markup=after_run_kb(url),
            )
        else:
            await call.message.edit_text(
                "❌ Retry failed. Check token/repo settings.",
                reply_markup=back_to_menu_kb(),
            )

    @router.callback_query(F.data == "menu")
    async def cb_menu(call: CallbackQuery):
        await call.answer()
        await call.message.edit_text(
            "👋 <b>QA Automation Bot</b>\n\n"
            "Manage your test pipeline directly from Telegram.\n"
            "Choose an action below:",
            reply_markup=main_menu_kb(),
        )

    return router
