from typing import Optional

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🚀 Run ALL", callback_data="run:all"),
    )
    builder.row(
        InlineKeyboardButton(text="🖥 Run UI",  callback_data="run:ui"),
        InlineKeyboardButton(text="🔌 Run API", callback_data="run:api"),
        InlineKeyboardButton(text="🔁 Run E2E", callback_data="run:e2e"),
    )
    builder.row(
        InlineKeyboardButton(text="📊 Status", callback_data="status"),
    )
    return builder.as_markup()


def after_run_kb(run_url: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔁 Retry",       callback_data="retry"),
        InlineKeyboardButton(text="📊 Status",      callback_data="status"),
    )
    builder.row(
        InlineKeyboardButton(text="🔗 Open on GitHub", url=run_url),
    )
    return builder.as_markup()


def status_kb(run_url: str, allure_url: Optional[str] = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔄 Refresh",        callback_data="status"),
        InlineKeyboardButton(text="🔁 Retry",          callback_data="retry"),
    )
    builder.row(
        InlineKeyboardButton(text="🔗 Open on GitHub", url=run_url),
    )
    if allure_url:
        builder.row(
            InlineKeyboardButton(text="📊 Allure Report", url=allure_url),
        )
    builder.row(
        InlineKeyboardButton(text="🏠 Main Menu",      callback_data="menu"),
    )
    return builder.as_markup()


def back_to_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🏠 Main Menu", callback_data="menu"))
    return builder.as_markup()