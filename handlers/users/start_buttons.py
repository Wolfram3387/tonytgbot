import json

from aiogram import types
from aiogram.dispatcher.storage import FSMContext

from data.config import admins
from filters import IsPrivate, IsNotAdmin
from handlers.users.functions import add_to_db
from loader import dp, users_db, variants_db
from keyboards.default import u_theory, u_menu, u_variants_categories, u_cancel_1, a_edit_users_db, a_cancel_1, \
    a_edit_variants_db, a_menu, AdminButtons, UserButtons


# ================================================================================================
# ============================================== USERS ===========================================
# ================================================================================================


@dp.message_handler(IsPrivate(), IsNotAdmin(), text=UserButtons.menu, state='*')
async def show_menu(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(message.text, reply_markup=u_menu)


@dp.message_handler(IsPrivate(), IsNotAdmin(), text=UserButtons.theory)
async def show_theory(message: types.Message):
    await message.answer('Выбери раздел', reply_markup=u_theory)


@dp.message_handler(IsPrivate(), IsNotAdmin(), text=UserButtons.statistic)
async def send_statistic(message: types.Message):
    await message.answer('Пока сбор статистики не работает')


@dp.message_handler(IsPrivate(), IsNotAdmin(), text=UserButtons.send_answers)
async def send_answers(message: types.Message, state: FSMContext):
    await add_to_db(message)    # TODO УБРАТЬ в скором времени
    await state.set_state('choice_of_variant_category')
    await message.answer('Выберите категорию варианта, на который Вы хотите отправить ответы',
                         reply_markup=u_variants_categories)


@dp.message_handler(IsPrivate(), IsNotAdmin(), text=[
    UserButtons.format_ege, UserButtons.format_oge, UserButtons.format_test, UserButtons.format_programming,
    UserButtons.format_other], state='choice_of_variant_category')
async def request_id_or_title(message: types.Message, state: FSMContext):
    """Отправляет ID и названия вариантов из категории, выбранной пользователем.
    Запрашивает ID или название варианта, на который пользователь хочет отправить ответы"""

    association = {UserButtons.format_ege: 'EGE', UserButtons.format_oge: 'OGE', UserButtons.format_test: 'TEST',
                   UserButtons.format_programming: 'PROG', UserButtons.format_other: 'OTHER'}
    if message.text in [UserButtons.format_ege, UserButtons.format_oge, UserButtons.format_test]:
        await state.set_state('getting_variant_title')

        variants = '\n'.join([f'{line[0]} - {line[1]}' for line in sorted(
            variants_db.select_all_variants(), key=lambda line: int(line[0])) if line[3] == association[message.text]])
        await message.answer(f'Вот все ID вариантов из выбранной категории и их названия:\n{variants}')
        await message.answer(
            'Отправьте мне ID или полное название варианта, на который Вы хотите дать ответы', reply_markup=u_cancel_1)

    elif message.text == UserButtons.format_programming:
        await state.set_state('input_of_files_with_programs')
        await message.answer(
            'Отправьте мне файлы с программами (имя файла должно соответствовать номеру задачи или в'
            ' программах должны быть комментарии, обозначающие номер/название задачи)', reply_markup=u_cancel_1
        )

    elif message.text == UserButtons.format_other:
        pass


# =================================================================================================
# ============================================== ADMINS ===========================================
# =================================================================================================


@dp.message_handler(IsPrivate(), text=[AdminButtons.edit_users_info,
                                       AdminButtons.edit_variants_info], user_id=admins)
async def edit_selection(message: types.Message, state: FSMContext):
    text = message.text
    if text == AdminButtons.edit_users_info:
        await state.set_state('entering_id_to_editing_UsersInfo')
        await message.answer(
            'Отправьте мне id пользователя, у которого Вы хотите что-то изменить', reply_markup=a_cancel_1)
    elif text == AdminButtons.edit_variants_info:
        await state.set_state('entering_title_to_editing_VariantsInfo')
        await message.answer(
            'Отправьте мне id или название варианта, в котором Вы хотите что-то изменить', reply_markup=a_cancel_1)


@dp.message_handler(IsPrivate(), content_types=['text'], user_id=admins, state=[
    'entering_id_to_editing_UsersInfo', 'entering_title_to_editing_VariantsInfo'])
async def check_variant_or_user_id(message: types.Message, state: FSMContext):
    """Получение ID пользователя или варианта для их последующего изменения в БД"""
    if message.text in 'Отмена':
        await state.finish()
        await message.answer(UserButtons.menu, reply_markup=a_menu)
        return

    state_name = await state.get_state()
    if state_name == 'entering_id_to_editing_UsersInfo':
        try:
            line = users_db.select_user(user_id=int(message.text))
            tt = line[2]    # tt - timetable
            student_name = line[1]
            msg = (
                f'Пользователь: {student_name}',
                f'Расписание на эту неделю:',
                '+=============+===========+',
                '|{0:^15}|{1:^13}|'.format("понедельник", tt["0"] if "0" in tt else "нет занятия").replace(' ', '_'),
                '|{0:^15}|{1:^13}|'.format("вторник", tt["1"] if "1" in tt else "нет занятия").replace(' ', '_'),
                '|{0:^15}|{1:^13}|'.format("среда", tt["2"] if "2" in tt else "нет занятия").replace(' ', '_'),
                '|{0:^16}|{1:^13}|'.format(" четверг ", tt["3"] if "3" in tt else "нет занятия").replace(' ', '_'),
                '|{0:^15}|{1:^13}|'.format("пятница", tt["4"] if "4" in tt else "нет занятия").replace(' ', '_'),
                '|{0:^15}|{1:^13}|'.format("суббота", tt["5"] if "5" in tt else "нет занятия").replace(' ', '_'),
                '|{0:^15}|{1:^13}|'.format("воскресенье", tt["6"] if "6" in tt else "нет занятия").replace(' ', '_'),
                '+=============+===========+',
                f'Готовится к: {line[3]}',
                f'Статус: {line[4] if line[4] else "Базовый"}',
                'Что Вы именно хотите изменить у пользователя?'
            )
            await state.update_data(student_id=int(message.text), student_name=student_name)
            await state.set_state('selection_for_editing_in_the_UsersInfo')
            await message.answer("\n".join(msg), reply_markup=a_edit_users_db)
        except TypeError:
            await message.answer('Пользователь с таким id не найден, попробуйте ещё раз')
        except ValueError:
            await message.answer('Некорректно введён id, попробуйте ещё раз')
    elif state_name == 'entering_title_to_editing_VariantsInfo':
        if message.text.isdigit():
            line = variants_db.select_variant(variant_id=int(message.text))
        else:
            line = variants_db.select_variant(title=message.text)
        if not line:
            await message.answer(f'Вариант "{message.text}" не найден, попробуйте ещё раз')
            return
        answers = '\n'.join(f'{number}) {answer}' for number, answer in json.loads(line[2]).items())
        additional = '\n'.join(f'{name} — {value}' for name, value in json.loads(line[6]).items())
        await state.set_state('selection_for_editing_in_the_VariantsInfo')
        await state.update_data(variant_line=line)
        await message.answer(
            f'Название: {line[1]}\nОтветы:\n{answers}\nТип: {line[3]}\nСтатус: {line[4]}\nИсточник: {line[5]}\n'
            f'Дополнения:\n{additional}\n\nЧто Вы хотите изменить в этом варианте?', reply_markup=a_edit_variants_db)
