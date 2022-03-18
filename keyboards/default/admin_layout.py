from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


class AdminButtons:
    menu = 'Меню 📒'
    cancel = 'Отмена'
    delete = 'Удалить'
    change = 'Изменить'
    yes = 'Да'
    no = 'Нет'
    add = 'Добавить'
    ege = 'ЕГЭ 📕'
    oge = 'ОГЭ 📗'
    programming = 'Программирование 👨🏻‍💻'

    name = 'Имя'
    timetable = 'Расписание'
    preparing_for = 'К чему готовится'
    achievements = 'Достижения'
    delete_user = 'Удалить пользователя'

    title = 'Название'
    answers = 'Ответы'
    additional = 'Дополнения'
    source = 'Источник'
    status = 'Статус'
    delete_variant = 'Удалить вариант'

    finish_newsletter = 'Завершить рассылку'
    cancel_newsletter = 'Отменить рассылку'
    check_all = 'Проверить все'
    check_selectively = 'Проверить выборочно'
    without_comment = 'Без комментария'
    check_next_student = 'Проверить следующего ученика'
    finish_checking = 'Завершить проверку'

    edit_users_info = 'Редактировать информацию о пользователях'
    check_homeworks = 'Проверить домашние работы'
    edit_variants_info = 'Редактировать информацию о вариантах'
    make_newsletter = 'Сделать рассылку 📣'
    add_info_to_new_variant = 'Добавить информацию на новый вариант'


a_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(AdminButtons.edit_users_info), KeyboardButton(AdminButtons.check_homeworks)
        ],
        [
            KeyboardButton(AdminButtons.edit_variants_info), KeyboardButton(AdminButtons.make_newsletter)
        ],
        [
            KeyboardButton(AdminButtons.add_info_to_new_variant)
        ],
    ],
    resize_keyboard=True,
)

a_what_to_check = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(AdminButtons.ege), KeyboardButton(AdminButtons.oge)
        ],
        [
            KeyboardButton(AdminButtons.programming), KeyboardButton(AdminButtons.menu)
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
            KeyboardButton(AdminButtons.name), KeyboardButton(AdminButtons.timetable)
        ],    # KeyboardButton('Валюта 1'), KeyboardButton('Валюта 2')
        [
            KeyboardButton(AdminButtons.preparing_for), KeyboardButton(AdminButtons.achievements)
        ],
        [
            KeyboardButton(AdminButtons.delete_user), KeyboardButton(AdminButtons.menu)
        ]
    ],
    resize_keyboard=True,
)

a_check_oge = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(AdminButtons.check_all),
        ],
        [
             KeyboardButton(AdminButtons.check_selectively)
        ],
        [
            KeyboardButton(AdminButtons.cancel)
        ]
    ]
)

a_edit_timetable_or_achievements = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(AdminButtons.delete)
        ],
        [
            KeyboardButton(AdminButtons.add)
        ],
        [
            KeyboardButton(AdminButtons.cancel)
        ]
    ],
    resize_keyboard=True,
)

a_delete_or_change = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(AdminButtons.delete)
        ],
        [
            KeyboardButton(AdminButtons.change)
        ],
        [
            KeyboardButton(AdminButtons.cancel)
        ]
    ],
    resize_keyboard=True,
)

a_yes_or_not = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(AdminButtons.yes)
        ],
        [
            KeyboardButton(AdminButtons.no)
        ]
    ],
    resize_keyboard=True,
)

a_delete_user_or_not = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(AdminButtons.delete)
        ],
        [
            KeyboardButton(AdminButtons.cancel)
        ]
    ],
    resize_keyboard=True,
)

a_no_comment = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(AdminButtons.without_comment)
        ],
    ],
    resize_keyboard=True,
)

a_edit_variants_db = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(AdminButtons.title), KeyboardButton(AdminButtons.answers)
        ],
        [
            KeyboardButton(AdminButtons.additional), KeyboardButton(AdminButtons.source), KeyboardButton(AdminButtons.status)
        ],
        [
            KeyboardButton(AdminButtons.delete_variant), KeyboardButton(AdminButtons.menu)
        ]
    ],
    resize_keyboard=True,
)

a_cancel_1 = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(AdminButtons.cancel)
        ]
    ],
    resize_keyboard=True,
)

a_finish_newsletter = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(AdminButtons.finish_newsletter)
        ],
        [
            KeyboardButton(AdminButtons.cancel_newsletter)
        ]
    ],
    resize_keyboard=True,
)

a_check_continue = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(AdminButtons.check_next_student)
        ],
        [
            KeyboardButton(AdminButtons.finish_checking)
        ]
    ],
    resize_keyboard=True,
)
