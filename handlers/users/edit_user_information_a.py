from aiogram import types
from aiogram.dispatcher import FSMContext

from filters import IsPrivate
from handlers.users._points_transfer import transfer_1, transfer_2
from keyboards.default import a_menu, a_cancel_1, a_edit_timetable_or_achievements, a_yes_or_not, a_edit_users_db, \
    AdminButtons, UserButtons
from loader import dp, users_db
from data.config import admins


@dp.message_handler(IsPrivate(), user_id=admins, state='selection_for_editing_in_the_UsersInfo', text=[
    AdminButtons.name, 'Валюта 1', 'Валюта 2', AdminButtons.preparing_for, AdminButtons.achievements, AdminButtons.timetable, AdminButtons.delete_user, UserButtons.menu
])
async def correction_db(message: types.Message, state: FSMContext):
    text = message.text
    if text == UserButtons.menu:
        await state.finish()
        await message.answer(UserButtons.menu, reply_markup=a_menu)
        return

    if text == AdminButtons.name:
        await state.set_state('editing_name')
        await message.answer(f'Отправьте мне его новое имя', reply_markup=a_cancel_1)

    elif text == AdminButtons.preparing_for:
        await state.set_state('editing_preparing_for')
        await message.answer('Отправьте мне к чему он теперь готовится:\n\nEGE или OGE', reply_markup=a_cancel_1)

    elif text == AdminButtons.achievements:
        data = await state.get_data()
        line = users_db.select_user(user_id=data['student_id'])
        achievements = line[5]
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

    elif text == AdminButtons.timetable:
        await state.set_state('what_to_change_in_the_timetable')
        await message.answer('Удалить что-то из расписания или добавить?',
                             reply_markup=a_edit_timetable_or_achievements)

    elif text == AdminButtons.delete_user:
        await state.set_state('delete_user_yes_or_not')
        data = await state.get_data()
        await message.answer(f'Вы действительно хотите удалить из базы данных пользователя {data["student_name"]}?',
                             reply_markup=a_yes_or_not)


@dp.message_handler(IsPrivate(), user_id=admins, text=[
    AdminButtons.delete, AdminButtons.add, 'Отмена'], state='add_or_delete_achievements')
async def blablabla(message: types.Message, state: FSMContext):
    text = message.text
    if text == 'Отмена':
        await state.set_state('selection_for_editing_in_the_UsersInfo')
        await message.answer(text, reply_markup=a_edit_users_db)
        return

    data = await state.get_data()
    name = data['student_name']
    if text == AdminButtons.add:
        await state.set_state('add_achievement')
        await message.answer(f'Отправьте мне название достижения, которое Вы хотите добавить пользователю {name}',
                             reply_markup=a_cancel_1)

    elif text == AdminButtons.delete:
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
    achievements = line[5]
    name = data['student_name']

    if state_name == 'add_achievement':
        if text in achievements:
            achievements[text] += 1
        else:
            achievements[text] = 1
        users_db.update_data(user_id=data['student_id'], achievements=achievements)

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
            users_db.update_data(user_id=data['student_id'], achievements=achievements)
        except KeyError:
            await message.answer(f'Достижения {text} нет у пользователя {name}, попробуйте ещё раз')


@dp.message_handler(IsPrivate(), user_id=admins, text=[AdminButtons.yes, AdminButtons.no], state='delete_user_yes_or_not')
async def blablabla(message: types.Message, state: FSMContext):
    if message.text == AdminButtons.yes:
        data = await state.get_data()
        users_db.delete_user(user_id=data['student_id'])
        await state.finish()
        await message.answer(f'Пользователь {data["student_name"]} удалён', reply_markup=a_menu)
    elif message.text == AdminButtons.no:
        await state.set_state('selection_for_editing_in_the_UsersInfo')
        await message.answer('Хорошо, не удаляю', reply_markup=a_edit_users_db)


@dp.message_handler(IsPrivate(), user_id=admins, text=[
    AdminButtons.delete, AdminButtons.add, 'Отмена'], state='what_to_change_in_the_timetable')
async def blablabla(message: types.Message, state: FSMContext):
    text = message.text

    if text == 'Отмена':
        await state.set_state('selection_for_editing_in_the_UsersInfo')
        await message.answer('Отмена', reply_markup=a_edit_users_db)
        return

    if text == AdminButtons.delete:
        await state.set_state('deleting_in_timetable')
        await message.answer(
            'Отправьте мне день/дни, который(-ые) Вы хотите удалить из расписания в формате:\n'
            'понедельник, среда, ...\n\nИЛИ\n\nпн, ср, сб, ...\n\nЛибо всё просто через пробел, либо через '
            'запятую с пробелом', reply_markup=a_cancel_1)

    elif text == AdminButtons.add:
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

    if state_name == 'editing_name':
        try:
            new_name = text
            if new_name == '':
                raise ValueError
            users_db.update_data(user_id=user_id, name=new_name)
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
        users_db.update_data(user_id=user_id, preparation_for=preparation_for)
        await state.set_state('selection_for_editing_in_the_UsersInfo')
        await message.answer(
            f'Статус подготовки ученика {name} изменён!\nТеперь он готовится к: «{preparation_for}»',
            reply_markup=a_edit_users_db)

    elif state_name == 'editing_achievements':
        line = users_db.select_user(user_id=user_id)
        achievements = line[5]
        if text in achievements:
            achievements[text] += 1
        else:
            achievements[text] = 1
        users_db.update_data(user_id=user_id, achievements=achievements)
        await state.set_state('selection_for_editing_in_the_UsersInfo')
        await message.answer(f'Достижение «{text}» успешно добавлено пользователю {name}', reply_markup=a_edit_users_db)
        # TODO добавить обработку ошибок

    elif state_name == 'deleting_in_timetable':
        line = users_db.select_user(user_id=user_id)
        timetable = line[2]
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

        users_db.update_data(user_id=user_id, timetable=timetable)
        await state.set_state('selection_for_editing_in_the_UsersInfo')
        await message.answer('\n'.join(msg), reply_markup=a_edit_users_db)

    elif state_name == 'adding_in_timetable':
        # TODO добавить обработку ошибок
        try:
            line = users_db.select_user(user_id=user_id)
            timetable = line[2]
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

        users_db.update_data(user_id=user_id, timetable=timetable)
        await state.set_state('selection_for_editing_in_the_UsersInfo')
        await message.answer('\n'.join(msg), reply_markup=a_edit_users_db)

    elif state_name == 'deleting_user':
        pass
