import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from config import load_config
from services.github import GitHubService
from handlers.commands import setup_commands_router
from handlers.callbacks import setup_callbacks_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    config = load_config()

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher()

    github = GitHubService(
        token=config.github_token,
        repo=config.repo,
        workflow_id=config.workflow_id,
        branch=config.github_branch,
    )

    dp.include_router(setup_commands_router(github))
    dp.include_router(setup_callbacks_router(github))

    await bot.set_my_commands([
        BotCommand(command="start", description="Main menu"),
        BotCommand(command="run_all", description="Run all tests"),
        BotCommand(command="run_ui", description="Run UI tests"),
        BotCommand(command="run_api", description="Run API tests"),
        BotCommand(command="run_e2e", description="Run E2E tests"),
        BotCommand(command="run_integration", 
                   description="Run Integration tests"),
        BotCommand(command="status", description="Check last run status"),
    ])

    logger.info("Bot started. Polling…")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
