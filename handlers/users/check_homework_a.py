import json
from aiogram import types
from aiogram.dispatcher import FSMContext

from filters import IsPrivate
from handlers.users._points_transfer import MAX_PRIMARY_POINTS_FOR_OGE, OGE_TRANSFER, EGE_POINTS_FOR_NUMBERS, \
    EGE_TRANSFER
from keyboards.default import a_what_to_check, a_menu, a_check_oge, a_check_continue, a_cancel_1
from loader import dp, bot, users_db
from data.config import admins


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


@dp.message_handler(IsPrivate(), user_id=admins, content_types=['text'], state=[
    'SINGLE_how_many_points_were_received', 'NOT_SINGLE_how_many_points_were_received'
])
async def correction_db(message: types.Message, state: FSMContext):
    """Админ отправляет сообщение о том, сколько баллов было получено учеником (при наличии решённой второй части)"""
    text = message.text

    if text == 'Отмена':
        await state.finish()
        await message.answer(text, reply_markup=a_menu)
        return
    try:
        points_for_2_part = {}
        for line in message.text.split('\n'):
            line = line.strip()
            number, points = line.split()
            points_for_2_part[number] = int(points)
        for i in ('13', '14', '15'):
            if i not in points_for_2_part:
                points_for_2_part[i] = 0
    except ValueError:    # Обработка некорректного ввода ответов
        await message.answer(f'Неправильный ввод, попробуйте ещё раз', reply_markup=a_cancel_1)
        return

    state_name = await state.get_state()
    data = await state.get_data()
    checking_student_id = data['checking_student_id']

    line = users_db.select_user(user_id=checking_student_id)
    requests = json.loads(line[9])
    checking_student_name = line[1]
    for key in requests:
        if key.startswith('oge_'):
            variant_info = requests[key]
            tasks_solved = variant_info['tasks_solved'] + sum([1 if i != 0 else 0 for i in points_for_2_part.values()])
            correct_answers = len(variant_info['correct_answers']) + 3
            results = variant_info['results']
            primary_points = variant_info['primary_points'] + sum(points_for_2_part.values())
            max_primary_points = MAX_PRIMARY_POINTS_FOR_OGE
            secondary_points = OGE_TRANSFER[primary_points]

            # Отправляем долгожданные результаты вместе со второй частью ученику
            await bot.send_message(checking_student_id, '\n'.join(
                    f'{_number}) {_answer} - {"✅" if _result else "❌"}' for _number, _answer, _result in
                    results) + f'\n13) {points_for_2_part["13"]}\n14) {points_for_2_part["14"]}\n15) '
                               f'{points_for_2_part["15"]}'
                    f'\n\nВы решили правильно {tasks_solved} из {correct_answers} задач!\n\n'
                    f'Набрано баллов: {primary_points} из {max_primary_points},'
                    f' что равно {round(primary_points / max_primary_points * 100, 1)}%\n\n'
                    f'Оценка: {secondary_points}')
            # TODO обновить статистику в БД

            # Удаляем из requests вариант для проверки и очищаем state_data админа
            await state.finish()
            del requests[key]
            users_db.update_data(user_id=checking_student_id, change=('requests', json.dumps(requests)))

            if state_name == 'NOT_SINGLE_how_many_points_were_received':
                await state.finish()
                await state.set_state('next_check_or_stop')
                await message.answer(f'Ученик {checking_student_name} оценен. Хотите проверить следующую работу?',
                                     reply_markup=a_check_continue)

            elif state_name == 'SINGLE_how_many_points_were_received':
                await state.finish()
                await message.answer(f'Ученик {checking_student_name} оценен', reply_markup=a_menu)

            return
