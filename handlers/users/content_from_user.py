from aiogram import types
from aiogram.dispatcher import FSMContext

from data.config import admins
from filters import IsPrivate, IsNotAdmin
from keyboards.default import u_menu, u_cancel_1, u_finish_entering, u_variants_categories, u_cancel_2, UserButtons
from loader import dp, users_db, variants_db, bot
from ._points_transfer import EGE_TRANSFER, EGE_POINTS_FOR_NUMBERS, OGE_TRANSFER, OGE_POINTS_FOR_NUMBERS, \
    MAX_PRIMARY_POINTS_FOR_OGE
from .functions import check_answers


@dp.message_handler(IsNotAdmin(), IsPrivate(), content_types=['photo', 'document', 'text'], state=[
    'input_of_files_with_programs', 'input_of_other_files', 'entering_documents'
])
async def get_photo(message: types.Message, state: FSMContext):
    content_type = message.content_type
    user_data = await state.get_data()

    if content_type == 'photo':
        if message.photo[-1].file_size > 20971520:   # 20971520 = 20 * 1024 * 1024 = 20 * 2^20 - перевод в байты
            await message.reply('Фото превышает 20 Мб')
            return
        photo_id = message.photo[-1].file_id
        if 'photo_ids' not in user_data:
            new_photo_ids = [photo_id]
            await state.update_data(photo_ids=new_photo_ids)
            # await state.set_state('repeat_oge_files_input')
        else:
            new_photo_ids = user_data['photo_ids']
            new_photo_ids.append(photo_id)
            await state.update_data(photo_ids=new_photo_ids)

        await message.reply('Фото успешно загружено', reply_markup=u_finish_entering)

    elif content_type == 'document':
        if message.document.file_size > 20971520:
            await message.reply('Файл превышает 20 Мб')
            return
        file_id = message.document.file_id

        if 'file_ids' not in user_data:
            new_file_ids = [file_id]
            await state.update_data(file_ids=new_file_ids)
        else:
            new_file_ids = user_data['file_ids']
            new_file_ids.append(file_id)
            await state.update_data(file_ids=new_file_ids)

        await message.reply('Файл успешно загружен', reply_markup=u_finish_entering)

    elif content_type == 'text':
        text = message.text

        if text == UserButtons.cancel:
            await state.set_state('choice_of_variant_category')
            await message.answer(text, reply_markup=u_variants_categories)

        elif text == UserButtons.finish_entering:
            user_id = message.from_user.id
            await state.finish()
            await message.answer('Ваш вариант успешно отправлен на проверку, ожидайте результатов!', reply_markup=u_menu)

            # Добавляем в requests всю информацию и ждём проверки от админа
            requests = users_db.select_user(user_id=user_id)[9]
            try:
                i = max((int(key.split('_')[1]) if key.startswith('prog_') else 0 for key in requests))
            except ValueError:
                i = 0
            requests[f'prog_{i+1}'] = {
                "photo_ids": user_data['photo_ids'] if 'photo_ids' in user_data else dict(),
                "file_ids": user_data['file_ids'] if 'file_ids' in user_data else dict(),
            }
            users_db.update_data(user_id=user_id, requests=requests)
            await bot.send_message(
                admins[0], f'Ученик {message.from_user.full_name} отправил(а) вариант по программированию на проверку!')


@dp.message_handler(IsNotAdmin(), IsPrivate(), content_types=['text'], state=[
    'entering_all_ege_answers', 'entering_test_oge_answers', 'entering_short_answers'
])
async def send_statistic(message: types.Message, state: FSMContext):
    """Получение всех тестовых ответов"""
    if message.text == UserButtons.cancel:
        await state.finish()
        await message.answer(UserButtons.menu, reply_markup=u_menu)
        return

    user_data = await state.get_data()
    variant_title, variant_id = user_data['variant_title'], user_data['variant_id']

    try:
        results, primary_points, tasks_solved = await check_answers(
            msg_with_answers=message, variant_id=user_data['variant_id'], variant_title=user_data['variant_title'])
    except ValueError:  # Обработка некорректного ввода ответов
        await message.answer(f'Неправильный ввод, попробуйте ещё раз')
        return

    state_name = await state.get_state()
    await state.update_data(variant_title=variant_title, variant_id=variant_id, tasks_solved=tasks_solved,
                            results=results, primary_points=primary_points)

    if state_name == 'entering_all_ege_answers':
        await state.set_state('other_files_to_check')
        await message.answer('Ответы сохранены, теперь Вы можете отправить мне файлы или фотографии с решениями',
                             reply_markup=u_cancel_2)

    elif state_name == 'entering_test_oge_answers':
        await state.set_state('oge_files_input')
        await message.answer(
            'Ответы сохранены, теперь Вы можете отправить мне файлы с задачами 13-15 или просто фотографии с решениями',
            reply_markup=u_cancel_2)

    elif state_name == 'entering_short_answers':    # Вывод ответов на обычный вариант
        await message.answer(
            '\n'.join(f'{_number}) {_answer} - {"✅" if _result else "❌"}' for _number, _answer, _result in results)
        )


@dp.message_handler(IsNotAdmin(), IsPrivate(), content_types=['text'], state='getting_variant_title')
async def send_statistic(message: types.Message, state: FSMContext):
    if message.text == UserButtons.cancel:
        await state.finish()
        await message.answer(message.text, reply_markup=u_menu)
        return

    variant_id, variant_title, *_ = variants_db.select_variant(variant_id=message.text, title=message.text)

    for variant_info in variants_db.select_all_variants():
        if variant_info[1].lower() == variant_title or variant_info[0] == variant_id:
            await state.update_data(variant_title=variant_title, variant_id=variant_id)

            # Если это вариант ЕГЭ: переводим на ввод всех ответов, потом на ввод доп. файлов
            if variant_info[3] == 'EGE':
                await state.set_state('entering_all_ege_answers')
                await message.answer('Введите ответы в формате:\n1) 123\n2) wzyx\n. . .', reply_markup=u_cancel_1)

            # Если это вариант ОГЭ: переводим на ввод кратких ответов, потом на ввод файлов для задач 13, 14, 15
            elif variant_info[3] == 'OGE':
                await state.set_state('entering_test_oge_answers')
                await message.answer(
                    'Введите краткие ответы для задач 1-12 в формате:\n1) 123\n2) abc\n. . .', reply_markup=u_cancel_1)

            # Если это обычный тест, то переводим на ввод кратких ответов
            elif variant_info[3] == 'TEST':
                await state.set_state('entering_short_answers')
                await message.answer(
                    'Введите ответы в формате:\n1) 123\n2) abc\n. . .',
                    reply_markup=u_cancel_1
                )

            # Если это другое, то переводим на ввод файлов
            elif variant_info[3] == 'OTHER':
                await state.set_state('input_of_other_files')
                await message.answer(
                    'Отправьте мне файлы с решенными задачами (имя файла должно соответствовать номеру'
                    ' задачи или в самом файле должен быть обозначен номер задачи)',
                    reply_markup=u_cancel_1
                )
            break
    else:
        # Сообщаем пользователю, если его вариант не нашёлся в БД:
        await message.answer(
            'Такого варианта пока нет. Пожалуйста, удостоверьтесь в правильности ввода и попробуйте ещё раз',
            reply_markup=u_cancel_1
        )


@dp.message_handler(IsNotAdmin(), IsPrivate(), content_types=['document', 'photo', 'text'], state=[
    'other_files_to_check', 'repeat_other_files_to_check'
])
async def send_statistic(message: types.Message, state: FSMContext):
    content_type = message.content_type
    name = message.from_user.full_name.title()
    text = message.text
    user_data = await state.get_data()
    variant_title = user_data['variant_title']
    variant_id = user_data['variant_id']

    if not variant_id or not variant_title:
        line = variants_db.select_variant(variant_id=variant_id, title=variant_title)
        variant_id = line[0]
        variant_title = line[1]

    if text in (UserButtons.finish_entering, UserButtons.skip):
        tasks_solved = user_data['tasks_solved']
        results = user_data['results']
        primary_points = user_data['primary_points']
        max_primary_points = sum(EGE_POINTS_FOR_NUMBERS.values())
        secondary_points = EGE_TRANSFER[primary_points]

        await state.finish()
        await message.answer(
            'Ваш результат:\n' +
            '\n'.join(f'{_number}) {_answer} - {"✅" if _result else "❌"}' for _number, _answer, _result in results))

        await message.answer(
                f'Вы решили правильно {tasks_solved} из {len(EGE_POINTS_FOR_NUMBERS)} задач!\n\n'
                f'Набрано первичных баллов: {primary_points} из {max_primary_points},'
                f' что равно {round(primary_points/max_primary_points*100, 1)}%\n\n'
                f'На реальном экзамене Вы бы набрали {secondary_points} из 100 баллов!', reply_markup=u_menu)

        # сохраняем вариант в requests как ege_{variant_id}
        user_line = users_db.select_user(user_id=message.from_user.id)
        requests = user_line[9]
        requests[f'ege_{variant_id}'] = {
            "photo_ids": user_data['photo_ids'] if 'photo_ids' in user_data else dict(),
            "file_ids": user_data['file_ids'] if 'file_ids' in user_data else dict(),
            "tasks_solved": user_data['tasks_solved'],
            "results": user_data['results'],
            "primary_points": user_data['primary_points']
        }
        users_db.update_data(user_id=message.from_user.id, requests=requests)
        await bot.send_message(admins[0], f'Ученик {user_line[1]} выполнил(а) работу "{variant_title}"')
        return

    elif text in (UserButtons.cancel, UserButtons.cancel_entering):
        await state.finish()
        await message.answer(text, reply_markup=u_menu)
        return

    state_name = await state.get_state()
    line = variants_db.select_variant(title=variant_title, variant_id=variant_id)

    if content_type == 'photo':
        if message.photo[-1].file_size > 20971520:  # 20971520 = 20 * 1024 * 1024 = 20 * 2^20 - перевод в байты
            await message.reply('Фото превышает 20 Мб')
            return
        photo_id = message.photo[-1].file_id

        if state_name == 'other_files_to_check':
            await state.set_state('repeat_other_files_to_check')
            await state.update_data(photo_ids=[photo_id])
        elif state_name == 'repeat_other_files_to_check':
            user_data['photo_ids'].append(photo_id)
            await state.update_data(photo_ids=user_data['photo_ids'])

        await message.reply('Фото успешно загружено', reply_markup=u_finish_entering)

    elif content_type == 'document':
        if message.document.file_size > 20971520:
            await message.reply('Файл превышает 20 Мб')
            return
        file_id = message.document.file_id

        if state_name == 'other_files_to_check':
            await state.set_state('repeat_other_files_to_check')
            await state.update_data(file_ids=[file_id])
        elif state_name == 'repeat_other_files_to_check':
            user_data['file_ids'].append(file_id)
            await state.update_data(photo_ids=user_data['file_ids'])

        await message.reply('Файл успешно загружен', reply_markup=u_finish_entering)
    if state_name == 'other_files_to_check':
        await state.set_state('repeat_other_files_to_check')


@dp.message_handler(IsNotAdmin(), IsPrivate(), content_types=['document', 'photo', 'text'], state=[
    'oge_files_input', 'repeat_oge_files_input'
])
async def send_statistic(message: types.Message, state: FSMContext):
    content_type = message.content_type
    name = message.from_user.full_name.title()
    text = message.text
    user_data = await state.get_data()
    user_id = message.from_user.id
    user_line = users_db.select_user(user_id=user_id)
    variant_id = user_data['variant_id']
    variant_title = user_data['variant_title']
    if not variant_id:
        variant_id = user_line[0]

    if text == UserButtons.finish_entering:    # Если ученик отправил задачи второй части на проверку
        await state.finish()
        await message.answer('Ваш вариант успешно отправлен на проверку, ожидайте результатов!', reply_markup=u_menu)

        # Добавляем в requests всю информацию по варианту и ждём проверки от админа
        requests = user_line[9]
        requests[f'oge_{variant_id}'] = {
            "photo_ids": user_data['photo_ids'] if 'photo_ids' in user_data else dict(),
            "file_ids": user_data['file_ids'] if 'file_ids' in user_data else dict(),
            "tasks_solved": user_data['tasks_solved'],
            "results": user_data['results'],
            "primary_points": user_data['primary_points']
        }
        users_db.update_data(user_id=user_id, requests=requests)
        await bot.send_message(admins[0], f'Ученик {user_line[1]} выполнил(а) работу "{variant_title}"')
        return

    elif text == UserButtons.skip:    # Если ученик НЕ отправил задачи второй части на проверку
        tasks_solved = user_data['tasks_solved']
        results = user_data['results']
        primary_points = user_data['primary_points']
        max_primary_points = MAX_PRIMARY_POINTS_FOR_OGE
        secondary_points = OGE_TRANSFER[primary_points]

        await state.finish()
        await message.answer(
            'Ваш результат:\n' +
            '\n'.join(f'{_number}) {_answer} - {"✅" if _result else "❌"}' for _number, _answer, _result in results))

        await message.answer(
            f'Вы решили правильно {tasks_solved} из {len(OGE_POINTS_FOR_NUMBERS) + 3} задач!\n\n'
            f'Набрано баллов: {primary_points} из {max_primary_points},'
            f' что равно {round(primary_points / max_primary_points * 100, 1)}%\n\n'
            f'На реальном экзамене Вы получили бы оценку: {secondary_points}', reply_markup=u_menu)

        # Сохраняем результаты варианта как oge_{variant_id}
        requests = user_line[9]
        requests[f'oge_{variant_id}'] = {
            "tasks_solved": user_data['tasks_solved'],
            "results": user_data['results'],
            "primary_points": user_data['primary_points']
        }
        users_db.update_data(user_id=user_id, requests=requests)
        await bot.send_message(admins[0], f'Ученик {user_line[1]} выполнил(а) работу "{variant_title}"')
        return

    elif text in (UserButtons.cancel, UserButtons.cancel_entering):
        await state.finish()
        await message.answer(text, reply_markup=u_menu)
        return

    if content_type == 'photo':
        if message.photo[-1].file_size > 20971520:  # 20971520 = 20 * 1024 * 1024
            await message.reply('Фото превышает 20 Мб')
            return
        photo_id = message.photo[-1].file_id
        if 'photo_ids' not in user_data:
            new_photo_ids = [photo_id]
            await state.update_data(photo_ids=new_photo_ids)
            # await state.set_state('repeat_oge_files_input')
        else:
            new_photo_ids = user_data['photo_ids']
            new_photo_ids.append(photo_id)
            await state.update_data(photo_ids=new_photo_ids)

        await message.reply('Фото успешно загружено', reply_markup=u_finish_entering)

    elif content_type == 'document':
        if message.document.file_size > 20971520:
            await message.reply('Файл превышает 20 Мб')
            return
        file_id = message.document.file_id

        if 'file_ids' not in user_data:
            new_file_ids = [file_id]
            await state.update_data(file_ids=new_file_ids)
            # await state.set_state('repeat_oge_files_input')
        else:
            new_file_ids = user_data['file_ids']
            new_file_ids.append(file_id)
            await state.update_data(file_ids=new_file_ids)

        await message.reply('Файл успешно загружен', reply_markup=u_finish_entering)
