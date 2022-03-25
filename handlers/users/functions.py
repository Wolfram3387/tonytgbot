import asyncio
from datetime import datetime
from random import randint

from aiogram.types.message import Message
from sqlalchemy.exc import IntegrityError

from loader import users_db, variants_db
from handlers.users._points_transfer import EGE_POINTS_FOR_NUMBERS, OGE_POINTS_FOR_NUMBERS


async def check_answers(msg_with_answers: Message, variant_title: str = None, variant_id: int = None):
    answers = dict()  # number: answer (str: str)
    for line in msg_with_answers.text.split('\n'):
        line = line.strip()
        for separator in (") ", ": ", ". ", " - ", " – ", ")", ":", " "):
            if separator in line:
                number, answer = line.replace('#', '').replace('№', '').split(separator)
                answers[number] = answer
                break

    results, primary_points, tasks_solved = list(), 0, 0  # Example results = [(1, 123, True), (2, abcd, False)]
    # results[0] - номер задачи, results[1] - ответ ученика, results[2] - правильный ответ или нет
    variant_info = variants_db.select_variant(variant_id=variant_id, title=variant_title)
    correct_answers = variant_info[2]
    variant_type = variant_info[3]
    for number, correct_answer in correct_answers.items():
        if number in answers:
            results.append((number, answers[number], correct_answer == answers[number].lower().strip()))
            if results[-1][2]:
                tasks_solved += 1
                if variant_type == 'EGE':
                    primary_points += EGE_POINTS_FOR_NUMBERS[results[-1][0]]
                elif variant_type == 'OGE':
                    primary_points += OGE_POINTS_FOR_NUMBERS[results[-1][0]]
        else:
            results.append((number, 'Нет ответа', False))
    return results, primary_points, tasks_solved


async def add_to_db(message: Message):
    try:
        users_db.add_user(
            user_id=message.from_user.id,
            name=message.from_user.full_name
        )
    except IntegrityError:
        pass


async def watch_notifications(dp, delay=5):
    """Каждые delay минут проверяет начало занятия и
    отправляет напоминание за час до занятий"""
    notifications = (    # name - имя ученика, time - время занятия (00:00)
        '🔔 {name}, напоминаю, что сегодня в {time} у тебя запланировано занятие по информатике!',
        '{name}, я уверен, что ты помнишь всё... 🧘🏽\nНо моя задача напомнить о сегодняшнем занятии в {time}!',
        '📚 {name}, надеюсь, ты уже выполнил(а) все задания, ведь сегодня в {time} у тебя занятие!'
    )
    while True:
        today_weekday = datetime.today().weekday()   # 0 - monday, 6 - sunday
        for user_id, name, timetable in ((line[0], line[1], line[2]) for line in users_db.select_all_users()):
            if today_weekday in timetable.keys():
                time_before_lesson = datetime.today().hour * 60 + datetime.today().minute -\
                                     timetable[today_weekday].hour * 60 - timetable[today_weekday].minute
                if time_before_lesson < 70:    # Напоминание о начале занятия за час
                    lesson_time = timetable[today_weekday]
                    kwargs = dict(name=name, time=f'{lesson_time.hour}:{lesson_time.minute}')
                    await dp.bot.send_message(
                        user_id, notifications[randint(0, len(notifications)-1)].format(**kwargs))
        await asyncio.sleep(delay*60)
