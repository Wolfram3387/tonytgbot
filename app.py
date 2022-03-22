# from handlers.users.functions import watch_notifications
from utils.set_bot_commands import set_default_commands


async def on_startup(dp):
    import filters
    # import middlewares
    filters.setup(dp)
    # middlewares.setup(dp)

    from utils.notify_admins import on_startup_notify

    await on_startup_notify(dp)
    await set_default_commands(dp)


async def on_shutdown(dp):
    from utils.notify_admins import on_shutdown_notify
    await on_shutdown_notify(dp)


if __name__ == '__main__':
    from aiogram import executor
    from handlers import dp

    # thread = threads.to_thread(watch_notifications, kwargs=dict(dp=dp))    # 1 поток (дополнительный)
    # thread.start()
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)    # 2 поток (основной)
# 123