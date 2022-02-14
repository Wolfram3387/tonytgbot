from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

a_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Редактировать информацию о пользователях'), KeyboardButton('Проверить домашние работы')
        ],
        [
            KeyboardButton('Редактировать информацию о вариантах'), KeyboardButton('Сделать рассылку 📣')
        ],
        [
            KeyboardButton('Добавить информацию на новый вариант')
        ],
    ],
    resize_keyboard=True,
)

a_what_to_check = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Варианты  ЕГЭ'), KeyboardButton('Варианты ОГЭ')
        ],
        [
            KeyboardButton('Программирование'), KeyboardButton('Меню 📒')
        ],
        # [
        #     KeyboardButton('Другое'), KeyboardButton('Тестовые варианты')
        # ]
    ],
    resize_keyboard=True,
)

a_edit_users_db = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Имя'), KeyboardButton('Расписание')
        ],    # KeyboardButton('Валюта 1'), KeyboardButton('Валюта 2')
        [
            KeyboardButton('К чему готовится'), KeyboardButton('Достижения')
        ],
        [
            KeyboardButton('Удалить пользователя'), KeyboardButton('Меню 📒')
        ]
    ],
    resize_keyboard=True,
)

a_check_oge = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Проверить все'),
        ],
        [
             KeyboardButton('Проверить выборочно')
        ],
        [
            KeyboardButton('Отмена')
        ]
    ]
)

a_edit_timetable_or_achievements = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Удалить')
        ],
        [
            KeyboardButton('Добавить')
        ],
        [
            KeyboardButton('Отмена')
        ]
    ],
    resize_keyboard=True,
)

a_delete_or_change = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Удалить')
        ],
        [
            KeyboardButton('Изменить')
        ],
        [
            KeyboardButton('Отмена')
        ]
    ],
    resize_keyboard=True,
)

a_yes_or_not = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Да')
        ],
        [
            KeyboardButton('Нет')
        ]
    ],
    resize_keyboard=True,
)

a_delete_user_or_not = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Удалить')
        ],
        [
            KeyboardButton('Отмена')
        ]
    ],
    resize_keyboard=True,
)

a_no_comment = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Без комментария')
        ],
    ],
    resize_keyboard=True,
)

a_edit_variants_db = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Название'), KeyboardButton('Ответы')
        ],
        [
            KeyboardButton('Дополнения'), KeyboardButton('Источник'), KeyboardButton('Статус')
        ],
        [
            KeyboardButton('Удалить вариант'), KeyboardButton('Меню 📒')
        ]
    ],
    resize_keyboard=True,
)

a_cancel_1 = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Отмена')
        ]
    ],
    resize_keyboard=True,
)

a_finish_newsletter = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Завершить рассылку')
        ],
        [
            KeyboardButton('Отменить рассылку')
        ]
    ],
    resize_keyboard=True,
)

a_check_continue = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Проверить следующего ученика')
        ],
        [
            KeyboardButton('Завершить проверку')
        ]
    ],
    resize_keyboard=True,
)
