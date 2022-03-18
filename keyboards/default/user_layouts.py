from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


class UserButtons:
    menu = 'Меню 📒'
    cancel = 'Отменить'
    back = 'Назад'
    finish_entering = 'Завершить ввод'
    cancel_entering = 'Отменить ввод'
    skip = 'Пропустить'
    send_answers = 'Отправить ответы 📩'
    variants = 'Варианты 🗂'
    statistic = 'Статистика 📊'
    theory = 'Теория 🔎'
    ege = 'ЕГЭ 📕'
    oge = 'ОГЭ 📗'
    programming = 'Программирование 👨🏻‍💻'
    format_ege = 'Вариант в формате ЕГЭ 📕'
    format_oge = 'Вариант в формате ОГЭ 📗'
    format_programming = 'Вариант по программированию 👨🏻‍💻'
    format_test = 'Обычный тест 📔'
    format_other = 'Другое 📓'


u_menu = ReplyKeyboardMarkup(
    keyboard=[
        # [
        #     KeyboardButton(b_variants), KeyboardButton(b_theory)
        # ],
        [
            KeyboardButton(UserButtons.send_answers),  # KeyboardButton(b_statistic)
        ]
    ],
    resize_keyboard=True,
)

u_theory = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(UserButtons.ege)
        ],
        [
            KeyboardButton(UserButtons.oge)
        ],
        [
            KeyboardButton(UserButtons.programming)
        ],
        [
            KeyboardButton(UserButtons.menu)
        ]
    ],
    resize_keyboard=True,
)

u_oge_numbers = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Задание 1'), KeyboardButton('Задание 2'),
            KeyboardButton('Задание 3'), KeyboardButton('Задание 4')
        ],
        [
            KeyboardButton('Задание 5'), KeyboardButton('Задание 6'),
            KeyboardButton('Задание 7'), KeyboardButton('Задание 8')
        ],
        [
            KeyboardButton('Задание 9'), KeyboardButton('Задание 10'),
            KeyboardButton('Задание 11'), KeyboardButton('Задание 12')
        ],
        [
            KeyboardButton('Задание 13'), KeyboardButton('Задание 14'),
            KeyboardButton('Задание 15'), KeyboardButton(UserButtons.menu)
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

u_ege_numbers = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Задание 1'), KeyboardButton('Задание 2'),
            KeyboardButton('Задание 3'), KeyboardButton('Задание 4'),
            KeyboardButton('Задание 5'), KeyboardButton('Задание 6')
        ],
        [
            KeyboardButton('Задание 7'), KeyboardButton('Задание 8'),
            KeyboardButton('Задание 9'), KeyboardButton('Задание 10'),
            KeyboardButton('Задание 11'), KeyboardButton('Задание 12')
        ],
        [
            KeyboardButton('Задание 13'), KeyboardButton('Задание 14'),
            KeyboardButton('Задание 15'), KeyboardButton('Задание 16'),
            KeyboardButton('Задание 17'), KeyboardButton('Задание 18')
        ],
        [
            KeyboardButton('Задание 19'), KeyboardButton('Задание 20'),
            KeyboardButton('Задание 21'), KeyboardButton('Задание 22'),
            KeyboardButton('Задание 23'), KeyboardButton('Задание 24')
        ],
        [
            KeyboardButton('Задание 25'), KeyboardButton('Задание 26'),
            KeyboardButton('Задание 27'), KeyboardButton(UserButtons.menu)
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

u_variants_categories = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(UserButtons.format_ege), KeyboardButton(UserButtons.format_oge)
        ],
        [
            KeyboardButton(UserButtons.format_programming), KeyboardButton(UserButtons.menu)
        ],
        # [
        #     KeyboardButton(UserButtons.format_other), KeyboardButton(UserButtons.format_test)
        # ],
    ],
    resize_keyboard=True,
)

u_cancel_1 = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(UserButtons.cancel)
        ],
    ],
    resize_keyboard=True,
)

u_cancel_2 = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(UserButtons.skip)
        ],
    ],
    resize_keyboard=True,
)

u_finish_entering = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(UserButtons.finish_entering)
        ],
        [
            KeyboardButton(UserButtons.cancel_entering)
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)
