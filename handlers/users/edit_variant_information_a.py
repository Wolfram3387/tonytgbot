from aiogram import types
from aiogram.dispatcher import FSMContext

from filters import IsPrivate
from keyboards.default import a_menu, a_cancel_1, a_edit_timetable_or_achievements, a_delete_or_change, a_yes_or_not, \
    a_edit_variants_db, UserButtons, AdminButtons
from loader import dp, variants_db
from data.config import admins


@dp.message_handler(IsPrivate(), user_id=admins, state='selection_for_editing_in_the_VariantsInfo', text=[
    AdminButtons.title, AdminButtons.answers, AdminButtons.additional, AdminButtons.source, AdminButtons.status, AdminButtons.delete_variant, UserButtons.menu
])
async def correction_db(message: types.Message, state: FSMContext):
    text = message.text
    if text == UserButtons.menu:
        await state.finish()
        await message.answer(text, reply_markup=a_menu)
        return

    data = await state.get_data()
    line = data['variant_line']

    if text == AdminButtons.title:
        await state.set_state('editing_title')
        await message.answer(f'Отправьте мне новое название варианта', reply_markup=a_cancel_1)

    elif text == AdminButtons.answers:
        await state.set_state('editing_answers')
        gen = (f'{number}) {answer}\n' for number, answer in line[2].items())
        msg = ''.join(gen) + '\nОтправьте мне новые ответы в формате:\n1) 123\n2) wzyx\n. . .\nИли просто через пробел'
        await message.answer(msg, reply_markup=a_cancel_1)

    elif text == AdminButtons.additional:
        await state.set_state('delete_or_add_additional')
        await message.answer('Удалить или добавить дополнение?', reply_markup=a_edit_timetable_or_achievements)

    elif text == AdminButtons.status:
        await state.set_state('change_or_delete_status')
        await message.answer('Удалить или изменить статус?', reply_markup=a_delete_or_change)

    elif text == AdminButtons.source:
        await state.set_state('change_or_delete_source')
        await message.answer('Удалить или изменить источник?', reply_markup=a_delete_or_change)

    elif text == AdminButtons.delete_variant:
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

    if text == AdminButtons.delete:
        await state.set_state('selection_for_editing_in_the_VariantsInfo')
        await message.answer('Статус успешно удалён', reply_markup=a_edit_variants_db)
        data = await state.get_data()
        line = data['variant_line']
        variants_db.update_data(_variant_id=line[0], _title=line[1], status=None)

    elif text == AdminButtons.change:
        await state.set_state('editing_satus')
        await message.answer('Отправьте мне новый статус для варианта', reply_markup=a_cancel_1)


@dp.message_handler(IsPrivate(), user_id=admins, content_types=['text'], state='change_or_delete_source')
async def correction_db(message: types.Message, state: FSMContext):
    text = message.text
    if text == 'Отмена':
        await state.set_state('selection_for_editing_in_the_VariantsInfo')
        await message.answer('Отмена', reply_markup=a_edit_variants_db)
        return

    if text == AdminButtons.delete:
        await state.set_state('selection_for_editing_in_the_VariantsInfo')
        await message.answer('Источник успешно удалён', reply_markup=a_edit_variants_db)
        data = await state.get_data()
        line = data['variant_line']
        variants_db.update_data(_variant_id=line[0], _title=line[1], source=None)

    elif text == AdminButtons.change:
        await state.set_state('editing_source')
        await message.answer('Отправьте мне новый источник для варианта', reply_markup=a_cancel_1)


@dp.message_handler(IsPrivate(), user_id=admins, content_types=['text'], state='delete_variant_yes_or_not')
async def correction_db(message: types.Message, state: FSMContext):
    if message.text == AdminButtons.yes:
        data = await state.get_data()
        line = data['variant_line']
        await state.set_state('selection_for_editing_in_the_VariantsInfo')
        await message.answer(f'Вариант {line[1]} удалён из базы данных', reply_markup=a_edit_variants_db)
        variants_db.delete_variant(variant_id=line[0], title=line[1])

    elif message.text == AdminButtons.no:
        await state.set_state('selection_for_editing_in_the_VariantsInfo')
        await message.answer('Хорошо, не удаляю', reply_markup=a_edit_variants_db)


@dp.message_handler(IsPrivate(), user_id=admins, content_types=['text'], state='delete_or_add_additional')
async def correction_db(message: types.Message, state: FSMContext):
    text = message.text
    if text == 'Отмена':
        await state.set_state('selection_for_editing_in_the_VariantsInfo')
        await message.answer(text, reply_markup=a_edit_variants_db)
        return

    if text == AdminButtons.delete:
        await state.set_state('deleting_additional')
        await message.answer('Отправьте мне название дополнения, которое нужно удалить (оно удалится всего 1 раз)',
                             reply_markup=a_cancel_1)

    elif text == AdminButtons.add:
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
        additional = line[6]
        try:
            additional[text] -= 1
            t = additional[text]
            if additional[text] == 0:
                del additional[text]
            variants_db.update_data(_variant_id=line[0], _title=line[1], additional=additional)
            await state.set_state('selection_for_editing_in_the_VariantsInfo')
            line[6] = additional
            await state.update_data(variant_line=line)
            await message.answer(
                f'Дополнение {text} удалено. Теперь у варианта "{line[1]}" их: {t}', reply_markup=a_edit_variants_db)
        except KeyError:
            await message.answer(f'У варианта "{line[1]}" не найдено дополнения {text}, попробуйте ещё раз')

    elif state_name == 'adding_additional':
        print(line[6], type(line[6]))
        additional = line[6]
        try:
            additional[text] += 1
            t = additional[text]
        except KeyError:
            additional[text] = 1
            t = 1
        line[6] = additional
        variants_db.update_data(_variant_id=line[0], _title=line[1], additional=additional)
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

        line[2] = answers
        await state.set_state('selection_for_editing_in_the_VariantsInfo')
        await message.answer(f'Ответы на вариант "{line[1]}" изменены', reply_markup=a_edit_variants_db)
        variants_db.update_data(_variant_id=line[0], _title=line[1], answers=answers)

    # Сохраняем изменённую информацию о варианте
    await state.update_data(variant_line=line)
