import logging

import aiogram.utils.exceptions
from aiogram import Dispatcher

from data.config import admins
from keyboards.default import a_menu, u_menu


async def on_startup_notify(dp: Dispatcher):
    from loader import users_db, bot
    for admin_id in admins:
        try:
            await dp.bot.send_message(admin_id, "Бот запущен", reply_markup=a_menu)

        except Exception as err:
            logging.exception(err)

    users = users_db.select_all_users()
    for user_id in (line[0] for line in users):
        try:
            await bot.send_message(
                user_id, 'Меню 📒', disable_notification=True, disable_web_page_preview=True, reply_markup=u_menu)

        except Exception as err:
            logging.exception(err)

        except aiogram.utils.exceptions.BotBlocked:
            users_db.delete_user(user_id=user_id)


async def on_shutdown_notify(dp: Dispatcher):
    for admin_id in admins:
        try:
            await dp.bot.send_message(admin_id, "Бот остановлен!")

        except Exception as err:
            logging.exception(err)
