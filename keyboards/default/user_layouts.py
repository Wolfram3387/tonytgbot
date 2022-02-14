from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

u_menu = ReplyKeyboardMarkup(
    keyboard=[
        # [
        #     KeyboardButton('Варианты 🗂'), KeyboardButton('Теория 🔎')
        # ],
        [
            KeyboardButton('Отправить ответы 📩'),  # KeyboardButton('Статистика 📊')
        ]
    ],
    resize_keyboard=True,
)

u_variants = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Вариант 1'), KeyboardButton('Вариант 2'),
            KeyboardButton('Вариант 3'), KeyboardButton('Вариант 4')
        ],
        [
            KeyboardButton('Вариант 5'), KeyboardButton('Вариант 6'),
            KeyboardButton('Вариант 7'), KeyboardButton('Вариант 8')
        ],
        [
            KeyboardButton('Вариант 9'), KeyboardButton('Вариант 10'),
            KeyboardButton('Вариант 11'), KeyboardButton('Вариант 12')
        ],
        [
            KeyboardButton('Вариант 13'), KeyboardButton('Вариант 14'),
            KeyboardButton('Вариант 15'), KeyboardButton('Вариант 16')
        ],
        [
            KeyboardButton('Вариант 17'), KeyboardButton('Вариант 18'),
            KeyboardButton('Вариант 19'), KeyboardButton('Вариант 20')
        ],
        [
            KeyboardButton('Меню 📒')
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

u_theory = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('ЕГЭ 📕')
        ],
        [
            KeyboardButton('ОГЭ 📗')
        ],
        [
            KeyboardButton('Программирование 👨🏻‍💻')
        ],
        [
            KeyboardButton('Меню 📒')
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
            KeyboardButton('Задание 15'), KeyboardButton('Меню 📒')
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
            KeyboardButton('Задание 27'), KeyboardButton('Меню 📒')
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

u_variants_categories = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Вариант в формате ЕГЭ 📕'), KeyboardButton('Вариант в формате ОГЭ 📗')
        ],
        [
            KeyboardButton('Вариант по программированию 👨🏻‍💻'), KeyboardButton('Меню 📒')
        ],
        # [
        #     KeyboardButton('Другое 📓'), KeyboardButton('Обычный тест 📔')
        # ],
    ],
    resize_keyboard=True,
)

u_cancel_1 = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Отменить')
        ],
    ],
    resize_keyboard=True,
)

u_cancel_2 = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Пропустить')
        ],
    ],
    resize_keyboard=True,
)

u_finish_entering = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Завершить ввод')
        ],
        [
            KeyboardButton('Отменить ввод')
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# KEYBOARD = {    # Максимальный id на данный момент: 017
#     'Меню 📒': ({
#         'Статистика 📊': (None, {'func': None, 'clr': 'blue', 'id': '001', 'br': 1}),
#         'Варианты 🗂': ({
#             'Вариант 1': (None, {'func': None, 'clr': 'green', 'id': '002', 'br': 1}),
#             'Вариант 2': (None, {'func': None, 'clr': 'green', 'id': '003', 'br': 1}),
#             'Вариант 3': (None, {'func': None, 'clr': 'green', 'id': '004', 'br': 1}),
#             'Вариант 4': (None, {'func': None, 'clr': 'green', 'id': '005', 'br': 1}),
#             'Меню 📒': (None, {'func': None, 'clr': 'red', 'back': '000', 'br': 0})
#         }, {'func': None, 'clr': 'blue', 'id': '006', 'br': 1}),
#         'Теория 🔎': ({
#             'ЕГЭ 📕': (None, {'func': None, 'clr': 'green', 'id': '007', 'br': 1}),
#             'ОГЭ 📗': ({
#                 'Задание 1': ('send_theory', {'func': None, 'clr': 'green', 'id': '008', 'br': 0}),
#                 'Задание 2': (None, {'func': None, 'clr': 'green', 'id': '009', 'br': 0}),
#                 'Задание 3': (None, {'func': None, 'clr': 'green', 'id': '010', 'br': 1}),
#                 'Задание 4': (None, {'func': None, 'clr': 'green', 'id': '011', 'br': 0}),
#                 'Задание 5': (None, {'func': None, 'clr': 'green', 'id': '012', 'br': 0}),
#                 'Задание 6': (None, {'func': None, 'clr': 'green', 'id': '013', 'br': 1}),
#                 'Назад ↩️': (None, {'func': None, 'clr': 'red', 'back': '016', 'br': 0})
#                        }, {'func': None, 'clr': 'green', 'id': '014', 'br': 1}),
#             'Программирование 👨🏻‍💻': (
#                 None, {'func': None, 'clr': 'green', 'id': '015', 'br': 1}),
#             'Меню 📒': (None, {'func': None, 'clr': 'red', 'back': '000', 'br': 0})
#         }, {'func': None, 'clr': 'blue', 'id': '016', 'br': 1}),
#         'Отправить ответы 📩': (None, {'func': None, 'clr': 'blue', 'id': '017', 'br': 0})
#     }, {'id': '000'})
# }
