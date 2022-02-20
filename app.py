import json
from time import time, sleep
from datetime import datetime
from random import randint
from sqlite3 import OperationalError
from threading import Thread

from utils.set_bot_commands import set_default_commands
from loader import users_db, variants_db


async def on_startup(dp):
    import filters
    # import middlewares
    filters.setup(dp)
    # middlewares.setup(dp)

    from utils.notify_admins import on_startup_notify

    try:
        users_db.create_table_users()
    except OperationalError:
        pass

    try:
        variants_db.create_variants_table()
    except OperationalError:
        pass

    await on_startup_notify(dp)
    await set_default_commands(dp)


async def on_shutdown(dp):
    from utils.notify_admins import on_shutdown_notify
    await on_shutdown_notify(dp)


async def watch_notifications(dp, delay=7):
    """Каждые delay минут проверяет начало занятия и
    отправляет напоминание за час до занятий"""
    notifications = (    # n - name, t - time
        '🔔 {n}, напоминаю, что сегодня в {t} у тебя запланировано занятие по информатике!',
        '{n}, я уверен, что ты помнишь всё... 🧘🏽\nНо моя задача напомнить о сегодняшнем занятии в {t}!',
        '📚 {n}, надеюсь, ты уже выполнил(а) все задания, ведь сегодня в {t} у тебя занятие!'
    )
    while True:
        today_number_of_the_week = datetime.today().weekday()   # 0 - monday, 6 - sunday
        generator = ((line[0], line[1], line[2]) for line in json.loads(users_db.select_all_users()))
        for user_id, name, timetable in generator:
            if timetable and today_number_of_the_week in timetable:
                _t = timetable[today_number_of_the_week]
                lesson_time = list(map(int, _t.replace(' ', '').split(':')))
                lesson_time_in_minutes = lesson_time[0] * 60 + lesson_time[1]
                today_time_in_minutes = datetime.now().hour * 60 + datetime.now().minute
                if 60 - delay < lesson_time_in_minutes - today_time_in_minutes <= 60:
                    first_name = name.split()[0]
                    await dp.bot.send_message(
                        user_id, notifications[randint(0, len(notifications)-1)].format(n=first_name, t=_t))

        sleep(420)


if __name__ == '__main__':
    from aiogram import executor
    from handlers import dp

    thread = Thread(target=watch_notifications, kwargs=dict(dp=dp))    # 1 поток (дополнительный)
    thread.start()
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)    # 2 поток (основной)
# some comment
