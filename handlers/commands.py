import asyncio
import logging

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from keyboards.inline import main_menu_kb, status_kb, back_to_menu_kb, after_run_kb
from services.github import GitHubService

logger = logging.getLogger(__name__)
router = Router()


def setup_commands_router(github: GitHubService) -> Router:

    # ------------------------------------------------------------------ #
    #  /start                                                            #
    # ------------------------------------------------------------------ #
    @router.message(CommandStart())
    async def cmd_start(message: Message):
        await message.answer(
            "👋 <b>QA Automation Bot</b>\n\n"
            "Manage your test pipeline directly from Telegram.\n"
            "Choose an action below:",
            reply_markup=main_menu_kb(),
        )

    # ------------------------------------------------------------------ #
    #  /run_all                                                          #
    # ------------------------------------------------------------------ #
    @router.message(Command("run_all"))
    async def cmd_run_all(message: Message):
        await _trigger(message, github, suite="all")

    # ------------------------------------------------------------------ #
    #  /run_ui                                                           #
    # ------------------------------------------------------------------ #
    @router.message(Command("run_ui"))
    async def cmd_run_ui(message: Message):
        await _trigger(message, github, suite="ui")

    # ------------------------------------------------------------------ #
    #  /run_api                                                          #
    # ------------------------------------------------------------------ #
    @router.message(Command("run_api"))
    async def cmd_run_api(message: Message):
        await _trigger(message, github, suite="api")

    # ------------------------------------------------------------------ #
    #  /run_e2e                                                          #
    # ------------------------------------------------------------------ #
    @router.message(Command("run_e2e"))
    async def cmd_run_e2e(message: Message):
        await _trigger(message, github, suite="e2e")

    # ------------------------------------------------------------------ #
    #  /run_integration                                                  #
    # ------------------------------------------------------------------ #
    @router.message(Command("run_e2e"))
    async def cmd_run_integration(message: Message):
        await _trigger(message, github, suite="integration")

    # ------------------------------------------------------------------ #
    #  /status                                                           #
    # ------------------------------------------------------------------ #
    @router.message(Command("status"))
    async def cmd_status(message: Message):
        await _send_status(message, github)

    return router


# ---------------------------------------------------------------------- #
#  Helpers                                                               #
# ---------------------------------------------------------------------- #

async def _trigger(message: Message, github: GitHubService, suite: str):
    label = suite.upper() if suite != "all" else "ALL"
    wait_msg = await message.answer(f"⏳ Triggering <b>{label}</b> tests…")

    ok = await github.dispatch_workflow(inputs={"test_suite": suite})

    if ok:
        run = await github.get_latest_run()
        url = run.html_url if run else "https://github.com"

        await wait_msg.edit_text(
            f"🚀 <b>{label}</b> pipeline triggered!\n\n"
            "I'll notify you when it's done.",
            reply_markup=after_run_kb(url),
        )

        if run:
            bot = message.bot
            chat_id = message.chat.id
            run_id = run.run_id

            async def notify(summary: str):
                try:
                    await bot.send_message(chat_id, summary)
                except Exception as exc:
                    logger.error("notify failed: %s", exc)

            asyncio.create_task(
                github.poll_until_complete(run_id=run_id, on_complete=notify)
            )
    else:
        await wait_msg.edit_text(
            "❌ Failed to trigger workflow.\n"
            "Check your <code>GITHUB_TOKEN</code> and repo settings.",
            reply_markup=back_to_menu_kb(),
        )


async def _send_status(message: Message, github: GitHubService):
    wait_msg = await message.answer("🔄 Fetching status…")
    text, url, allure_url = await github.get_status_text()

    if url:
        await wait_msg.edit_text(text, reply_markup=status_kb(url, allure_url))
    else:
        await wait_msg.edit_text(text, reply_markup=back_to_menu_kb())