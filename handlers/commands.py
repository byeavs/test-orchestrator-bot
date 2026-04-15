import logging

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from keyboards.inline import main_menu_kb
from services.github import GitHubService

logger = logging.getLogger(__name__)
router = Router()


def setup_commands_router(github: GitHubService) -> Router:
    
    @router.message(CommandStart())
    async def cmd_start(message: Message):
        await message.answer(
            "👋 <b>QA Flow</b>\n\n"
            "Manage test pipeline.\n"
            "Choose an action:",
            reply_markup=main_menu_kb(),
        )

    @router.message(Command("run_all"))
    async def cmd_run_all(message: Message):
        await _trigger(message, github, suite="all")

    @router.message(Command("run_ui"))
    async def cmd_run_ui(message: Message):
        await _trigger(message, github, suite="ui")

    @router.message(Command("run_api"))
    async def cmd_run_api(message: Message):
        await _trigger(message, github, suite="api")

    @router.message(Command("run_e2e"))
    async def cmd_run_e2e(message: Message):
        await _trigger(message, github, suite="e2e")

    @router.message(Command("status"))
    async def cmd_status(message: Message):
        await _send_status(message, github)

    return router

async def _trigger(message: Message, github: GitHubService, suite: str):
    from keyboards.inline import after_run_kb, back_to_menu_kb

    label = suite.upper() if suite != "all" else "ALL"
    wait_msg = await message.answer(f"⏳ Triggering <b>{label}</b> tests…")

    inputs = {} if suite == "all" else {"suite": suite}
    ok = await github.dispatch_workflow(inputs=inputs)

    if ok:
        run = await github.get_latest_run()
        url = run.html_url if run else "https://github.com"
        await wait_msg.edit_text(
            f"🚀 <b>{label}</b> pipeline triggered!\n\n"
            f"GitHub Actions is processing your request.",
            reply_markup=after_run_kb(url),
        )
    else:
        await wait_msg.edit_text(
            "❌ Failed to trigger workflow.\n"
            "Check your git token and settings.",
            reply_markup=back_to_menu_kb(),
        )


async def _send_status(message: Message, github: GitHubService):
    from keyboards.inline import status_kb, back_to_menu_kb

    wait_msg = await message.answer("🔄 Fetching status…")
    text, url = await github.get_status_text()

    if url:
        await wait_msg.edit_text(text, reply_markup=status_kb(url))
    else:
        await wait_msg.edit_text(text, reply_markup=back_to_menu_kb())
