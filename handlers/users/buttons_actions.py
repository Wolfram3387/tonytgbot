import json

from aiogram.types import ContentType
from data.config import admins
from handlers.users._points_transfer import MAX_PRIMARY_POINTS_FOR_OGE, OGE_TRANSFER, EGE_POINTS_FOR_NUMBERS, \
    EGE_TRANSFER
from loader import dp, users_db, variants_db, bot
from aiogram import types
from filters import IsPrivate, IsNotAdmin
from aiogram.dispatcher.storage import FSMContext

from keyboards.default import u_theory, u_menu, u_variants_categories, u_cancel_1, a_edit_users_db, a_cancel_1, \
    a_edit_variants_db, a_menu, a_edit_timetable_or_achievements, a_check_oge, a_check_continue, a_yes_or_not, \
    a_what_to_check, a_finish_newsletter, a_delete_or_change


# TODO измени названия функций

# ================================================================================================
# ============================================== USERS ===========================================
# ================================================================================================


@dp.message_handler(IsPrivate(), IsNotAdmin(), text='Меню 📒', state='*')
async def show_menu(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(message.text, reply_markup=u_menu)


@dp.message_handler(IsPrivate(), IsNotAdmin(), text='Теория 🔎')
async def show_theory(message: types.Message):
    await message.answer('Выбери раздел', reply_markup=u_theory)


@dp.message_handler(IsPrivate(), IsNotAdmin(), text='Статистика 📊')
async def send_statistic(message: types.Message):
    await message.answer('Пока сбор статистики не работает')


@dp.message_handler(IsPrivate(), IsNotAdmin(), text='Отправить ответы 📩')
async def send_statistic(message: types.Message, state: FSMContext):
    await state.set_state('choice_of_variant_category')
    await message.answer('Выберите категорию варианта, на который Вы хотите отправить ответы',
                         reply_markup=u_variants_categories)


@dp.message_handler(IsPrivate(), IsNotAdmin(), text=[
    'Вариант в формате ЕГЭ 📕', 'Вариант в формате ОГЭ 📗', 'Обычный тест 📔', 'Вариант по программированию 👨🏻‍💻',
    'Другое 📓'
], state='choice_of_variant_category')
async def send_statistic(message: types.Message, state: FSMContext):
    text = message.text
    if text in ['Вариант в формате ЕГЭ 📕', 'Вариант в формате ОГЭ 📗', 'Обычный тест 📔']:
        await state.set_state('getting_variant_title')
        # TODO нужно будет отправить доступные варианты EGE/OGE/TEST... в зависимости от выбора в message.text
        await message.answer(
            'Отправьте мне ID или полное название варианта, на который Вы хотите дать ответы', reply_markup=u_cancel_1)

    elif text == 'Вариант по программированию 👨🏻‍💻':
        await state.set_state('input_of_files_with_programs')
        await message.answer(
            'Отправьте мне файлы с программами (имя файла должно соответствовать номеру задачи или в'
            ' программах должны быть комментарии, обозначающие номер/название задачи)', reply_markup=u_cancel_1
        )

    elif text == 'Другое 📓':
        # TODO Доделать
        pass


# =================================================================================================
# ============================================== ADMINS ===========================================
# =================================================================================================


@dp.message_handler(IsPrivate(), text=['Сделать рассылку 📣'], user_id=admins)
async def spam(message: types.Message, state: FSMContext):
    await state.set_state('spam')
    await message.answer('Отправьте мне сообщения для рассылки (только текст или файлы)', reply_markup=a_cancel_1)


@dp.message_handler(IsPrivate(), text=['Редактировать информацию о пользователях',
                                       'Редактировать информацию о вариантах'], user_id=admins)
async def edit_selection(message: types.Message, state: FSMContext):
    text = message.text
    if text == 'Редактировать информацию о пользователях':
        await state.set_state('entering_id_to_editing_UsersInfo')
        await message.answer(
            'Отправьте мне id пользователя, у которого Вы хотите что-то изменить', reply_markup=a_cancel_1)
    elif text == 'Редактировать информацию о вариантах':
        await state.set_state('entering_title_to_editing_VariantsInfo')
        await message.answer(
            'Отправьте мне id или название варианта, в котором Вы хотите что-то изменить', reply_markup=a_cancel_1)


@dp.message_handler(IsPrivate(), content_types=['text'], user_id=admins, state=[
    'entering_id_to_editing_UsersInfo', 'entering_title_to_editing_VariantsInfo'
])
async def edit_selection(message: types.Message, state: FSMContext):
    if message.text in 'Отмена':
        await state.finish()
        await message.answer('Меню 📒', reply_markup=a_menu)
        return

    state_name = await state.get_state()
    if state_name == 'entering_id_to_editing_UsersInfo':
        try:
            line = users_db.select_user(user_id=int(message.text))
            tt = json.loads(line[2])    # tt - timetable
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


@dp.message_handler(IsPrivate(), user_id=admins, state='selection_for_editing_in_the_UsersInfo', text=[
    'Имя', 'Валюта 1', 'Валюта 2', 'К чему готовится', 'Достижения', 'Расписание', 'Удалить пользователя', 'Меню 📒'
])
async def correction_db(message: types.Message, state: FSMContext):
    text = message.text
    if text == 'Меню 📒':
        await state.finish()
        await message.answer('Меню 📒', reply_markup=a_menu)
        return

    if text == 'Имя':
        await state.set_state('editing_name')
        await message.answer(f'Отправьте мне его новое имя', reply_markup=a_cancel_1)

    elif text == 'К чему готовится':
        await state.set_state('editing_preparing_for')
        await message.answer('Отправьте мне к чему он теперь готовится:\n\nEGE или OGE', reply_markup=a_cancel_1)

    elif text == 'Достижения':
        data = await state.get_data()
        line = users_db.select_user(user_id=data['student_id'])
        achievements = json.loads(line[5])
        msg = [f'Текущий список достижений ученика {data["student_name"]}:']
        for achievement, count in achievements.items():
            msg.append(f'    {achievement}: {count}')
        if not achievements:
            msg.append('~ ~ ~ Пусто ~ ~ ~')
        msg.append('\nКак именно Вы хотите изменить их?')

        await state.set_state('add_or_delete_achievements')
        await message.answer('\n'.join(msg), reply_markup=a_edit_timetable_or_achievements)

    elif text == 'Валюта 1':
        # await state.set_state('editing_curr_1')
        # TODO доделать
        await message.answer('Пока эта фишка не применяется')

    elif text == 'Валюта 2':
        # await state.set_state('editing_curr_2')
        # TODO доделать
        await message.answer('Пока эта фишка не применяется')

    elif text == 'Расписание':
        await state.set_state('what_to_change_in_the_timetable')
        await message.answer('Удалить что-то из расписания или добавить?',
                             reply_markup=a_edit_timetable_or_achievements)

    elif text == 'Удалить пользователя':
        await state.set_state('delete_user_yes_or_not')
        data = await state.get_data()
        await message.answer(f'Вы действительно хотите удалить из базы данных пользователя {data["student_name"]}?',
                             reply_markup=a_yes_or_not)


@dp.message_handler(IsPrivate(), user_id=admins, text=[
    'Удалить', 'Добавить', 'Отмена'], state='add_or_delete_achievements')
async def blablabla(message: types.Message, state: FSMContext):
    text = message.text
    if text == 'Отмена':
        await state.set_state('selection_for_editing_in_the_UsersInfo')
        await message.answer(text, reply_markup=a_edit_users_db)
        return

    data = await state.get_data()
    name = data['student_name']
    if text == 'Добавить':
        await state.set_state('add_achievement')
        await message.answer(f'Отправьте мне название достижения, которое Вы хотите добавить пользователю {name}',
                             reply_markup=a_cancel_1)

    elif text == 'Удалить':
        await state.set_state('delete_achievement')
        await message.answer(f'Отправьте мне название достижения, которое Вы хотите убрать у пользователя'
                             f' {name}\n(это достижение уберётся только 1 раз)', reply_markup=a_cancel_1)


@dp.message_handler(IsPrivate(), user_id=admins, content_types='text', state=[
    'add_achievement', 'delete_achievement'])
async def blablabla(message: types.Message, state: FSMContext):
    text = message.text
    if text == 'Отмена':
        await state.set_state('selection_for_editing_in_the_UsersInfo')
        await message.answer(text, reply_markup=a_edit_users_db)
        return

    state_name = await state.get_state()
    data = await state.get_data()
    line = users_db.select_user(user_id=data['student_id'])
    achievements = json.loads(line[5])
    name = data['student_name']

    if state_name == 'add_achievement':
        if text in achievements:
            achievements[text] += 1
        else:
            achievements[text] = 1
        users_db.update_data(user_id=data['student_id'], change=('achievements', json.dumps(achievements)))

        await state.set_state('selection_for_editing_in_the_UsersInfo')
        await message.answer(f'Достижение {text} успешно добавлено пользователю {name}\n(теперь у него их'
                             f' {achievements[text]})', reply_markup=a_edit_users_db)

    elif state_name == 'delete_achievement':
        try:
            achievements[text] -= 1
            await state.set_state('selection_for_editing_in_the_UsersInfo')
            await message.answer(f'Достижение {text} успешно удалено у пользователя {name}\n(теперь у него их '
                                 f'{achievements[text]})', reply_markup=a_edit_users_db)
            if achievements[text] == 0:
                del achievements[text]
            users_db.update_data(user_id=data['student_id'], change=('achievements', json.dumps(achievements)))
        except KeyError:
            await message.answer(f'Достижения {text} нет у пользователя {name}, попробуйте ещё раз')


@dp.message_handler(IsPrivate(), user_id=admins, text=['Да', 'Нет'], state='delete_user_yes_or_not')
async def blablabla(message: types.Message, state: FSMContext):
    if message.text == 'Да':
        data = await state.get_data()
        users_db.delete_user(user_id=data['student_id'])
        await state.finish()
        await message.answer(f'Пользователь {data["student_name"]} удалён', reply_markup=a_menu)
    elif message.text == 'Нет':
        await state.set_state('selection_for_editing_in_the_UsersInfo')
        await message.answer('Хорошо, не удаляю', reply_markup=a_edit_users_db)


@dp.message_handler(IsPrivate(), user_id=admins, text=[
    'Удалить', 'Добавить', 'Отмена'], state='what_to_change_in_the_timetable')
async def blablabla(message: types.Message, state: FSMContext):
    text = message.text

    if text == 'Отмена':
        await state.set_state('selection_for_editing_in_the_UsersInfo')
        await message.answer('Отмена', reply_markup=a_edit_users_db)
        return

    if text == 'Удалить':
        await state.set_state('deleting_in_timetable')
        await message.answer(
            'Отправьте мне день/дни, который(-ые) Вы хотите удалить из расписания в формате:\n'
            'понедельник, среда, ...\n\nИЛИ\n\nпн, ср, сб, ...\n\nЛибо всё просто через пробел, либо через '
            'запятую с пробелом', reply_markup=a_cancel_1)

    elif text == 'Добавить':
        await state.set_state('adding_in_timetable')
        await message.answer(
            'Отправьте мне день/дни, который(-ые) Вы хотите добавить в расписание в формате:\n'
            'понедельник 10:00, среда 18:45, ...\n\nИЛИ\n\nпн 10:00, ср 19:10, сб 20:50, ...\n\nСтрого через запятую'
            ' с пробелом', reply_markup=a_cancel_1)


@dp.message_handler(IsPrivate(), user_id=admins, content_types=['text'], state=[
    'editing_name', 'editing_preparing_for', 'editing_achievements', 'editing_curr_1', 'editing_curr_2',
    'deleting_in_timetable', 'adding_in_timetable', 'deleting_user'
])
async def correction_db(message: types.Message, state: FSMContext):
    text = message.text
    if text in ('Назад', 'Отмена'):
        await state.set_state('selection_for_editing_in_the_UsersInfo')
        await message.answer(text, reply_markup=a_edit_users_db)
        return

    state_name = await state.get_state()
    data = await state.get_data()
    user_id = data['student_id']
    name = data['student_name']

    transfer_1 = {'пн': 0, 'вт': 1, 'ср': 2, 'чт': 3, 'пт': 4, 'сб': 5, 'вс': 6, 'понедельник': 0, 'вторник': 1,
                  'среда': 2, 'четверг': 3, 'пятница': 4, 'суббота': 5, 'воскресенье': 6}
    transfer_2 = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    transfer_3 = {'пн': 'Понедельник', 'вт': 'Вторник', 'ср': 'Среда', 'чт': 'Четверг',
                  'пт': 'Пятница', 'сб': 'Суббота', 'вс': 'Воскресенье'}

    if state_name == 'editing_name':
        try:
            new_name = text
            if new_name == '':
                raise ValueError
            users_db.update_data(user_id=user_id, change=('name', new_name))
            await state.set_state('selection_for_editing_in_the_UsersInfo')
            await state.update_data(student_name=new_name)
            await message.answer(f'Полное имя обновлено!\nНовое имя пользователя: {new_name}',
                                 reply_markup=a_edit_users_db)
        except ValueError:
            await message.answer('Некорректный ввод, попробуйте ещё раз!')

    elif state_name == 'editing_curr_1':
        await message.answer('Какая валюта? Эта фишка ещё не работает')

    elif state_name == 'editing_curr_2':
        await message.answer('Какая валюта? Эта фишка ещё не работает')

    elif state_name == 'editing_preparing_for':
        preparation_for = message.text
        users_db.update_data(user_id=user_id, change=('preparation_for', preparation_for))
        await state.set_state('selection_for_editing_in_the_UsersInfo')
        await message.answer(
            f'Статус подготовки ученика {name} изменён!\nТеперь он готовится к: «{preparation_for}»',
            reply_markup=a_edit_users_db)

    elif state_name == 'editing_achievements':
        line = users_db.select_user(user_id=user_id)
        achievements = json.loads(line[5])
        if text in achievements:
            achievements[text] += 1
        else:
            achievements[text] = 1
        users_db.update_data(user_id=user_id, change=('achievements', json.dumps(achievements)))
        await state.set_state('selection_for_editing_in_the_UsersInfo')
        await message.answer(f'Достижение «{text}» успешно добавлено пользователю {name}', reply_markup=a_edit_users_db)
        # TODO добавить обработку ошибок

    elif state_name == 'deleting_in_timetable':
        line = users_db.select_user(user_id=user_id)
        timetable = json.loads(line[2])
        for day in text.split(', ') if ', ' in text else text.split():
            try:
                if str(transfer_1[day.lower()]) in timetable:
                    del timetable[str(transfer_1[day.lower()])]
            except KeyError as err:
                await message.answer(f'неизвестный день недели {err}, попробуйте ещё раз')
                return

        msg = [f'Изменения успешно применены, новое расписание пользователя {name}:']
        for number, time in timetable.items():
            msg.append(f'    {transfer_2[int(number)]} - {time}')
        if not timetable:
            msg.append('~ ~ ~ Пусто ~ ~ ~')

        users_db.update_data(user_id=user_id, change=('timetable', json.dumps(timetable)))
        await state.set_state('selection_for_editing_in_the_UsersInfo')
        await message.answer('\n'.join(msg), reply_markup=a_edit_users_db)

    elif state_name == 'adding_in_timetable':
        # TODO добавить обработку ошибок
        try:
            line = users_db.select_user(user_id=user_id)
            timetable = json.loads(line[2])
            for new in text.split(', '):
                day, time = new.split()
                if day.lower() in transfer_1:
                    if str(transfer_1[day.lower()]) in timetable:
                        del timetable[str(transfer_1[day.lower()])]
                    timetable[transfer_1[day.lower()]] = time
                else:
                    raise ValueError    # неправильно указан день
        except ValueError:
            await message.answer('Неправильно указан день, попробуйте ещё раз')
            return

        msg = [f'Изменения успешно применены, новое расписание пользователя {name}:']
        for number, time in timetable.items():
            msg.append(f'    {transfer_2[int(number)]} - {time}')
        if not timetable:
            msg.append('~ ~ ~ Пусто ~ ~ ~')

        users_db.update_data(user_id=user_id, change=('timetable', json.dumps(timetable)))
        await state.set_state('selection_for_editing_in_the_UsersInfo')
        await message.answer('\n'.join(msg), reply_markup=a_edit_users_db)

    elif state_name == 'deleting_user':
        pass


@dp.message_handler(IsPrivate(), user_id=admins, state='selection_for_editing_in_the_VariantsInfo', text=[
    'Название', 'Ответы', 'Дополнения', 'Источник', 'Статус', 'Удалить вариант', 'Меню 📒'
])
async def correction_db(message: types.Message, state: FSMContext):
    text = message.text
    if text == 'Меню 📒':
        await state.finish()
        await message.answer(text, reply_markup=a_menu)
        return

    data = await state.get_data()
    line = data['variant_line']

    if text == 'Название':
        await state.set_state('editing_title')
        await message.answer(f'Отправьте мне новое название варианта', reply_markup=a_cancel_1)

    elif text == 'Ответы':
        await state.set_state('editing_answers')
        gen = (f'{number}) {answer}\n' for number, answer in json.loads(line[2]).items())
        msg = ''.join(gen) + '\nОтправьте мне новые ответы в формате:\n1) 123\n2) wzyx\n. . .\nИли просто через пробел'
        await message.answer(msg, reply_markup=a_cancel_1)

    elif text == 'Дополнения':
        await state.set_state('delete_or_add_additional')
        await message.answer('Удалить или добавить дополнение?', reply_markup=a_edit_timetable_or_achievements)

    elif text == 'Статус':
        await state.set_state('change_or_delete_status')
        await message.answer('Удалить или изменить статус?', reply_markup=a_delete_or_change)

    elif text == 'Источник':
        await state.set_state('change_or_delete_source')
        await message.answer('Удалить или изменить источник?', reply_markup=a_delete_or_change)

    elif text == 'Удалить вариант':
        await state.set_state('delete_variant_yes_or_not')
        await message.answer(
            f'Вы действительно хотите удалить "{line[1]}"?', reply_markup=a_yes_or_not)


@dp.message_handler(IsPrivate(), user_id=admins, content_types=['text'], state='change_or_delete_status')
async def correction_db(message: types.Message, state: FSMContext):
    text = message.text
    if text == 'Отмена':
        await state.set_state('selection_for_editing_in_the_VariantsInfo')
        await message.answer('Отмена', reply_markup=a_edit_variants_db)
        return

    if text == 'Удалить':
        await state.set_state('selection_for_editing_in_the_VariantsInfo')
        await message.answer('Статус успешно удалён', reply_markup=a_edit_variants_db)
        data = await state.get_data()
        line = data['variant_line']
        variants_db.update_data(_variant_id=line[0], _title=line[1], status=None)

    elif text == 'Изменить':
        await state.set_state('editing_satus')
        await message.answer('Отправьте мне новый статус для варианта', reply_markup=a_cancel_1)


@dp.message_handler(IsPrivate(), user_id=admins, content_types=['text'], state='change_or_delete_source')
async def correction_db(message: types.Message, state: FSMContext):
    text = message.text
    if text == 'Отмена':
        await state.set_state('selection_for_editing_in_the_VariantsInfo')
        await message.answer('Отмена', reply_markup=a_edit_variants_db)
        return

    if text == 'Удалить':
        await state.set_state('selection_for_editing_in_the_VariantsInfo')
        await message.answer('Источник успешно удалён', reply_markup=a_edit_variants_db)
        data = await state.get_data()
        line = data['variant_line']
        variants_db.update_data(_variant_id=line[0], _title=line[1], source=None)

    elif text == 'Изменить':
        await state.set_state('editing_source')
        await message.answer('Отправьте мне новый источник для варианта', reply_markup=a_cancel_1)


@dp.message_handler(IsPrivate(), user_id=admins, content_types=['text'], state='delete_variant_yes_or_not')
async def correction_db(message: types.Message, state: FSMContext):
    if message.text == 'Да':
        data = await state.get_data()
        line = data['variant_line']
        await state.set_state('selection_for_editing_in_the_VariantsInfo')
        await message.answer(f'Вариант {line[1]} удалён из базы данных', reply_markup=a_edit_variants_db)
        variants_db.delete_variant(variant_id=line[0], title=line[1])

    elif message.text == 'Нет':
        await state.set_state('selection_for_editing_in_the_VariantsInfo')
        await message.answer('Хорошо, не удаляю', reply_markup=a_edit_variants_db)


@dp.message_handler(IsPrivate(), user_id=admins, content_types=['text'], state='delete_or_add_additional')
async def correction_db(message: types.Message, state: FSMContext):
    text = message.text
    if text == 'Отмена':
        await state.set_state('selection_for_editing_in_the_VariantsInfo')
        await message.answer(text, reply_markup=a_edit_variants_db)
        return

    if text == 'Удалить':
        await state.set_state('deleting_additional')
        await message.answer('Отправьте мне название дополнения, которое нужно удалить (оно удалится всего 1 раз)',
                             reply_markup=a_cancel_1)

    elif text == 'Добавить':
        await state.set_state('adding_additional')
        await message.answer('Отправьте мне название дополнения, которое Вы хотите добавить (оно добавится 1 раз)',
                             reply_markup=a_cancel_1)


@dp.message_handler(IsPrivate(), user_id=admins, content_types=['text'], state=[
    'editing_title', 'editing_source', 'editing_satus', 'deleting_additional', 'adding_additional', 'editing_answers'
])
async def correction_db(message: types.Message, state: FSMContext):
    text = message.text
    if text == 'Отмена':
        await state.set_state('selection_for_editing_in_the_VariantsInfo')
        await message.answer('Отмена', reply_markup=a_edit_variants_db)
        return

    data = await state.get_data()
    line = list(data['variant_line'])
    state_name = await state.get_state()

    if state_name == 'editing_title':
        await state.set_state('selection_for_editing_in_the_VariantsInfo')
        line[1] = text
        await message.answer(f'Новое название варианта: {text}', reply_markup=a_edit_variants_db)
        variants_db.update_data(_variant_id=line[0], _title=line[1], title=text)

    elif state_name == 'editing_source':
        await state.set_state('selection_for_editing_in_the_VariantsInfo')
        line[5] = text
        await message.answer(f'Источник варианта "{line[1]}" изменён на: {text}', reply_markup=a_edit_variants_db)
        variants_db.update_data(_variant_id=line[0], _title=line[1], source=text)

    elif state_name == 'editing_satus':
        await state.set_state('selection_for_editing_in_the_VariantsInfo')
        line[4] = text
        await message.answer(f'Статус варианта "{line[1]}" изменён на: {text}', reply_markup=a_edit_variants_db)
        variants_db.update_data(_variant_id=line[0], _title=line[1], status=text)

    elif state_name == 'deleting_additional':
        additional = json.loads(line[6])
        try:
            additional[text] -= 1
            t = additional[text]
            if additional[text] == 0:
                del additional[text]
            variants_db.update_data(_variant_id=line[0], _title=line[1], additional=json.dumps(additional))
            await state.set_state('selection_for_editing_in_the_VariantsInfo')
            line[6] = json.dumps(additional)
            await state.update_data(variant_line=line)
            await message.answer(
                f'Дополнение {text} удалено. Теперь у варианта "{line[1]}" их: {t}', reply_markup=a_edit_variants_db)
        except KeyError:
            await message.answer(f'У варианта "{line[1]}" не найдено дополнения {text}, попробуйте ещё раз')

    elif state_name == 'adding_additional':
        print(line[6], type(line[6]))
        additional = json.loads(line[6])
        try:
            additional[text] += 1
            t = additional[text]
        except KeyError:
            additional[text] = 1
            t = 1
        line[6] = json.dumps(additional)
        variants_db.update_data(_variant_id=line[0], _title=line[1], additional=json.dumps(additional))
        await state.set_state('selection_for_editing_in_the_VariantsInfo')
        await message.answer(
            f'Дополнение "{text}" добавлено. Теперь у варианта "{line[1]}" их: {t}', reply_markup=a_edit_variants_db)

    elif state_name == 'editing_answers':
        answers = dict()  # number: answer (str: str)
        try:
            for _line in message.text.split('\n'):
                _line = _line.strip()
                if ') ' in _line:
                    number, answer = _line.split(') ')
                    answers[number] = answer
                else:
                    number, answer = _line.split()
                    answers[number] = answer
        except ValueError:
            await message.answer(f'Неправильный ввод, попробуйте ещё раз')
            return

        line[2] = json.dumps(answers)
        await state.set_state('selection_for_editing_in_the_VariantsInfo')
        await message.answer(f'Ответы на вариант "{line[1]}" изменены', reply_markup=a_edit_variants_db)
        variants_db.update_data(_variant_id=line[0], _title=line[1], answers=json.dumps(answers))

    # Сохраняем изменённую информацию о варианте
    await state.update_data(variant_line=line)


@dp.message_handler(IsPrivate(), user_id=admins, text='Проверить домашние работы')
async def correction_db(message: types.Message, state: FSMContext):
    await state.set_state('what_to_check_from_homework')
    await message.answer('Что именно Вы хотите проверить?', reply_markup=a_what_to_check)


@dp.message_handler(IsPrivate(), user_id=admins, state='what_to_check_from_homework', text=[
    'Варианты  ЕГЭ', 'Варианты ОГЭ', 'Тестовые варианты', 'Программирование', 'Другое', 'Меню 📒'])
async def correction_db(message: types.Message, state: FSMContext):    # TODO доделать
    text = message.text
    if text == 'Меню 📒':
        await state.finish()
        await message.answer(text, reply_markup=a_menu)
        return

    elif text == 'Варианты  ЕГЭ':
        new_state, new_layout = 'how_to_check_ege', a_check_oge
    elif text == 'Варианты ОГЭ':
        new_state, new_layout = 'how_to_check_oge', a_check_oge
    elif text == 'Тестовые варианты':
        new_state, new_layout = 'how_to_check_common_variant', a_check_oge
    elif text == 'Программирование':
        new_state, new_layout = 'how_to_check_programs', a_check_oge
    elif text == 'Другое':
        new_state, new_layout = 'how_to_check_other', a_check_oge

    await state.set_state(new_state)
    await message.answer('Как именно Вы хотите осуществить проверку?', reply_markup=new_layout)


@dp.message_handler(IsPrivate(), user_id=admins, text=[
    'Проверить все', 'Проверить выборочно', 'Отмена'], state=[
    'how_to_check_ege', 'how_to_check_oge', 'how_to_check_common_variant', 'how_to_check_programs', 'how_to_check_other'])
@dp.message_handler(IsPrivate(), user_id=admins, text=[
    'Проверить следующего ученика', 'Завершить проверку'], state='next_check_or_stop')
async def correction_db(message: types.Message, state: FSMContext):
    # Открываем БД, пробегаемся по requests и ищем запросы начинающиеся на 'oge_'
    text = message.text

    if text in ('Завершить проверку', 'Отмена'):
        await state.finish()
        await message.answer(text, reply_markup=a_menu)
        return

    state_name = await state.get_state()
    if text in ('Проверить все', 'Проверить следующего ученика'):
        data_of_all_users = users_db.select_all_users()
        admin_id = message.from_user.id
        for line in data_of_all_users:
            name = line[1]
            requests = json.loads(line[9])
            for key in requests:
                if key.startswith('oge_') and state_name == 'how_to_check_oge':
                    await state.update_data(checking_student_id=line[0])
                    await state.update_data(checking_student_name=name)

                    variant_info = requests[key]
                    photo_ids = variant_info['photo_ids'] if 'photo_ids' in variant_info else dict()
                    file_ids = variant_info['file_ids'] if 'file_ids' in variant_info else dict()
                    tasks_solved = variant_info['tasks_solved']
                    correct_answers = variant_info['correct_answers']
                    results = variant_info['results']
                    primary_points = variant_info['primary_points']
                    max_primary_points = MAX_PRIMARY_POINTS_FOR_OGE
                    secondary_points = OGE_TRANSFER[primary_points]
                    await message.answer(
                        '\n'.join(
                    f'{_number}) {_answer} - {"✅" if _result else "❌"}' for _number, _answer, _result in results)
                + f'\n\n{name} решил правильно {tasks_solved} из {len(correct_answers)} задач!\n\n'
                  f'Набрано баллов: {primary_points} из {max_primary_points},'
                  f' что равно {round(primary_points / max_primary_points * 100, 1)}%\n\n'
                  f'Оценка: {secondary_points}', reply_markup=a_check_continue)

                    if file_ids or photo_ids:
                        for file_id in file_ids:
                            await bot.send_document(admin_id, file_id)

                        for photo_id in photo_ids:
                            await bot.send_photo(admin_id, photo_id)

                        await state.set_state('NOT_SINGLE_how_many_points_were_received')
                        await message.answer(
                            f'Отправьте мне баллы ученика {name} за задачи 13-15 в формате:\n\n13 2\n14 3\n15 0',
                            reply_markup=a_cancel_1)
                    else:
                        await state.set_state('next_check_or_stop')
                        await message.answer('Проверить следующего?', reply_markup=a_check_continue)

                    del requests[key]
                    users_db.update_data(user_id=line[0], change=('requests', json.dumps(requests)))
                    return

                elif key.startswith('prog_') and state_name == 'how_to_check_programs':
                    await state.update_data(checking_student_id=line[0])
                    await state.update_data(checking_student_name=name)
                    await state.set_state('how_many_programs_have_been_solved')

                    variant_info = requests[key]
                    photo_ids = variant_info['photo_ids'],
                    file_ids = variant_info['file_ids'],

                    file_ids = file_ids[0] if len(
                        file_ids) != 0 else dict()  # TODO странная нормировка данных. Можно исправить
                    photo_ids = photo_ids[0] if len(photo_ids) != 0 else dict()

                    for file_id in file_ids:
                        await bot.send_document(admin_id, file_id)

                    for photo_id in photo_ids:
                        await bot.send_photo(admin_id, photo_id)

                    await message.answer(
                        f'Отправьте мне количество решённых задач у ученика {name} в формате:'
                        f'\n4/5\n(что значит 4 из 5 задач решено)\n', reply_markup=a_cancel_1)
                    return

                elif key.startswith('ege_') and state_name == 'how_to_check_ege':
                    await state.update_data(checking_student_id=line[0])
                    await state.update_data(checking_student_name=name)
                    await state.set_state('next_check_or_stop')

                    variant_info = requests[key]
                    photo_ids = variant_info['photo_ids'] if 'photo_ids' in variant_info else dict(),
                    file_ids = variant_info['file_ids'] if 'file_ids' in variant_info else dict(),
                    tasks_solved = variant_info['tasks_solved'],
                    correct_answers = variant_info['correct_answers'],
                    results = variant_info['results'],
                    primary_points = variant_info['primary_points']
                    max_primary_points = sum(EGE_POINTS_FOR_NUMBERS.values())
                    secondary_points = EGE_TRANSFER[primary_points]

                    await message.answer(
                        '\n'.join(
                            f'{_number}) {_answer} - {"✅" if _result else "❌"}' for _number, _answer, _result in
                            results[0])
                        + f'\n\n{name} решил(а) правильно {tasks_solved[0]} из {len(correct_answers[0])} задач!\n\n'
                          f'Набрано первичных баллов: {primary_points} из {max_primary_points},'
                          f' что равно {round(primary_points / max_primary_points * 100, 1)}%\n\n'
                          f'Во вторичных баллах это {secondary_points} из 100!', reply_markup=a_check_continue)

                    file_ids = file_ids[0] if len(
                        file_ids) != 0 else dict()  # TODO странная нормировка данных. Можно исправить
                    photo_ids = photo_ids[0] if len(photo_ids) != 0 else dict()
                    for file_id in file_ids:
                        await bot.send_document(admin_id, file_id)

                    for photo_id in photo_ids:
                        await bot.send_photo(admin_id, photo_id)

                    # Удаляем отправленный вариант из базы данных
                    del requests[key]
                    users_db.update_data(user_id=int(line[0]), change=('requests', json.dumps(requests)))
                    return

                elif key.startswith('test_') and state_name == 'how_to_check_common_variant':
                    return

                elif key.startswith('other_') and state_name == 'how_to_check_other':
                    return

        else:
            await state.finish()
            await message.answer('Все варианты проверены!', reply_markup=a_menu)

    elif text == 'Проверить выборочно':
        if state_name == 'how_to_check_oge':
            await state.set_state('enter_id_to_check_oge')
        elif state_name == 'how_to_check_programs':
            await state.set_state('enter_id_to_check_programs')
        elif state_name == 'how_to_check_ege':
            await state.set_state('enter_id_to_check_ege')
        elif state_name == 'how_to_check_common_variant':
            await state.set_state('enter_id_to_check_common_variant')
        elif state_name == 'how_to_check_other':
            await state.set_state('enter_id_to_check_other')

        await message.answer('Введите id пользователя, у которого хотите проверить вариант', reply_markup=a_cancel_1)


@dp.message_handler(IsPrivate(), user_id=admins, state=[
    'how_many_programs_have_been_solved', 'single_how_many_programs_have_been_solved'])
async def correction_db(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        await state.set_state('what_to_check_from_homework')
        await message.answer(message.text, reply_markup=a_what_to_check)
        return

    data = await state.get_data()
    state_name = await state.get_state()
    try:
        correct_programs, count_of_programs = map(int, message.text.replace(' ', '').split('/'))
        await bot.send_message(
            data['checking_student_id'],
            f'{data["checking_student_name"]}, учитель проверил Ваши программы и зачёл '
            f'{correct_programs} из {count_of_programs} задач')
        if state_name == 'how_many_programs_have_been_solved':
            await state.set_state('next_check_or_stop')
        elif state_name == 'single_how_many_programs_have_been_solved':
            await state.finish()
        await message.answer(
            f'Ученик {data["checking_student_name"]} проверен. Решено задач: {correct_programs} из {count_of_programs}',
            reply_markup=a_check_continue if state_name == 'how_many_programs_have_been_solved' else a_menu)
        line = users_db.select_user(user_id=int(data['checking_student_id']))
        requests = json.loads(line[9])
        for key in requests:
            if key.startswith('prog_'):
                key_to_delete = key
        del requests[key_to_delete]
        users_db.update_data(user_id=int(data['checking_student_id']), change=('requests', json.dumps(requests)))
    except:  # TODO добавить обработку ошибок
        await message.answer(f'Неправильный ввод, попробуйте ещё раз')


@dp.message_handler(IsPrivate(), user_id=admins, content_types=['text'], state='enter_id_to_check_oge')
async def correction_db(message: types.Message, state: FSMContext):
    """Ввод id пользователя для поиска его непроверенных работ ОГЭ"""
    text = message.text

    if text == 'Отмена':
        await state.finish()
        await message.answer(text, reply_markup=a_menu)
        return

    try:
        line = users_db.select_user(user_id=int(text))
        name = line[1]
        requests = json.loads(line[9])
        assert any(key.startswith('oge_') for key in requests)
    except AssertionError:
        await message.answer(f'У пользователя {name} нет непроверенных вариантов ОГЭ')
        return
    except TypeError:
        await message.answer('Пользователь с таким id не найден, попробуйте ещё раз')
        return

    for key in requests:
        if key.startswith('oge_'):
            await state.update_data(checking_student_id=line[0])
            await state.set_state('SINGLE_how_many_points_were_received')
            admin_id = message.from_user.id

            variant_info = requests[key]
            photo_ids = variant_info['photo_ids'],
            file_ids = variant_info['file_ids'],
            tasks_solved = variant_info['tasks_solved'],
            correct_answers = variant_info['correct_answers'],
            results = variant_info['results'],
            primary_points = variant_info['primary_points']
            max_primary_points = MAX_PRIMARY_POINTS_FOR_OGE
            secondary_points = OGE_TRANSFER[primary_points]

            await message.answer(
                'Предварительные результаты:' +
                '\n'.join(
                    f'{_number}) {_answer} - {"✅" if _result else "❌"}' for _number, _answer, _result in results[0])
                + f'\n\n{name} решил правильно {tasks_solved[0]} из {len(correct_answers[0])} задач!\n\n'
                  f'Набрано баллов: {primary_points} из {max_primary_points},'
                  f' что равно {round(primary_points / max_primary_points * 100, 1)}%\n\n'
                  f'Оценка: {secondary_points}', reply_markup=a_check_continue
            )

            file_ids = file_ids[0] if len(file_ids) != 0 else dict()  # TODO странная нормировка данных. Можно исправить
            photo_ids = photo_ids[0] if len(photo_ids) != 0 else dict()
            for file_id in file_ids:
                if file_id:
                    await bot.send_document(admin_id, file_id)

            for photo_id in photo_ids:
                if photo_id:
                    await bot.send_photo(admin_id, photo_id)

            await message.answer(f'Отправьте мне баллы ученика {name} за задачи 13-15 в формате:\n\n13 2\n14 3\n15 0',
                                 reply_markup=a_cancel_1)
            return


@dp.message_handler(IsPrivate(), user_id=admins, content_types=['text'], state='enter_id_to_check_programs')
async def correction_db(message: types.Message, state: FSMContext):
    """Ввод id пользователя для поиска его непроверенных задач по программированию"""
    text = message.text
    if text == 'Отмена':
        await state.finish()
        await message.answer(text, reply_markup=a_menu)
        return

    try:
        line = users_db.select_user(user_id=int(text))
        name = line[1]
        requests = json.loads(line[9])
        assert any(key.startswith('prog_') for key in requests)
    except AssertionError:
        await message.answer(f'У пользователя {name} нет непроверенных работ по программированию')
        return
    except TypeError:
        await message.answer('Пользователь с таким id не найден, попробуйте ещё раз')
        return

    for key in requests:
        if key.startswith('prog_'):
            await state.update_data(checking_student_id=line[0], checking_student_name=name)
            await state.set_state('how_many_programs_have_been_solved')
            admin_id = message.from_user.id

            variant_info = requests[key]
            photo_ids = variant_info['photo_ids'] if 'photo_ids' in variant_info else dict()
            file_ids = variant_info['file_ids'] if 'file_ids' in variant_info else dict()

            for file_id in file_ids:
                if file_id:
                    await bot.send_document(admin_id, file_id)

            for photo_id in photo_ids:
                if photo_id:
                    await bot.send_photo(admin_id, photo_id)

            await message.answer(f'Отправьте мне количество решённых задач ученика {name} в формате:\n3/4\n(что'
                                 f' означает, решено 3 из 4 задач)', reply_markup=a_cancel_1)
            return


@dp.message_handler(IsPrivate(), user_id=admins, content_types=['text'], state='enter_id_to_check_ege')
async def correction_db(message: types.Message, state: FSMContext):
    """Ввод id пользователя для просмотра его файлов ЕГЭ"""
    text = message.text
    if text == 'Отмена':
        await state.finish()
        await message.answer(text, reply_markup=a_menu)
        return

    try:
        line = users_db.select_user(user_id=int(text))
        name = line[1]
        requests = json.loads(line[9])
        assert any(key.startswith('ege_') for key in requests)
    except AssertionError:
        await message.answer(f'У пользователя {name} нет непроверенных работ ЕГЭ')
        return
    except TypeError:
        await message.answer('Пользователь с таким id не найден, попробуйте ещё раз')
        return

    for key in requests:
        if key.startswith('ege_'):
            await state.finish()
            admin_id = message.from_user.id

            variant_info = requests[key]
            photo_ids = variant_info['photo_ids'] if 'photo_ids' in variant_info else dict()
            file_ids = variant_info['file_ids'] if 'file_ids' in variant_info else dict()
            tasks_solved = variant_info['tasks_solved'],
            correct_answers = variant_info['correct_answers'],
            results = variant_info['results'],
            primary_points = variant_info['primary_points']
            max_primary_points = sum(EGE_POINTS_FOR_NUMBERS.values())
            secondary_points = EGE_TRANSFER[primary_points]

            await message.answer(
                '\n'.join(
                    f'{_number}) {_answer} - {"✅" if _result else "❌"}' for _number, _answer, _result in
                    results[0])
                + f'\n\n{name} решил(а) правильно {tasks_solved[0]} из {len(correct_answers[0])} задач!\n\n'
                  f'Набрано первичных баллов: {primary_points} из {max_primary_points},'
                  f' что равно {round(primary_points / max_primary_points * 100, 1)}%\n\n'
                  f'Во вторичных баллах это {secondary_points} из 100!', reply_markup=a_menu)

            file_ids = file_ids[0] if len(file_ids) != 0 else dict()  # TODO странная нормировка данных. Можно исправить
            photo_ids = photo_ids[0] if len(photo_ids) != 0 else dict()
            for file_id in file_ids:
                if file_id:
                    await bot.send_document(admin_id, file_id)

            for photo_id in photo_ids:
                if photo_id:
                    await bot.send_photo(admin_id, photo_id)

            return
