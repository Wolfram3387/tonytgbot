from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Запуск чата"),
        types.BotCommand("help", "Помощь"),
        types.BotCommand("menu", "Показать меню"),
        types.BotCommand("variants", "Показать ID вариантов"),
        types.BotCommand('whatsnew', "Что нового в обновлении?")
    ])
