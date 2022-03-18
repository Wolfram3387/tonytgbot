from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType

from filters import IsPrivate
from loader import dp, bot, users_db
from data.config import admins
from keyboards.default import a_cancel_1, a_menu, a_finish_newsletter, AdminButtons


@dp.message_handler(IsPrivate(), text=[AdminButtons.make_newsletter], user_id=admins)
async def spam(message: types.Message, state: FSMContext):
    await state.set_state('spam')
    await message.answer('Отправьте мне сообщения для рассылки (только текст или файлы)', reply_markup=a_cancel_1)


@dp.message_handler(IsPrivate(), state='spam', user_id=admins, content_types=ContentType.ANY)
async def start_spam(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        await state.finish()
        await message.answer('Отмена рассылки', reply_markup=a_menu)
        return
    events = [message]
    await state.update_data(events_to_send=events)
    await state.set_state('spam_continue')
    await message.answer('Вы можете отправить ещё что-то или завершить рассылку', reply_markup=a_finish_newsletter)


@dp.message_handler(IsPrivate(), state='spam_continue', user_id=admins, content_types=ContentType.ANY)
async def start_spam(message: types.Message, state: FSMContext):
    if message.text == AdminButtons.finish_newsletter:
        users = (line[0] for line in users_db.select_all_users())
        data = await state.get_data()
        for user in users:
            for event in data['events_to_send']:
                event_type = event.content_type
                try:
                    if event_type == ContentType.TEXT:
                        await bot.send_message(user, event.text)
                    elif event_type == ContentType.DOCUMENT:
                        await bot.send_document(user, event.document.file_id)
                except:   # TODO добавить обработку различных ошибок
                    pass

        await state.finish()
        await message.answer('Рассылка завершена', reply_markup=a_menu)
        return
    elif message.text == AdminButtons.cancel_newsletter:
        await state.finish()
        await message.answer('Рассылка отменена', reply_markup=a_menu)
        return

    data = await state.get_data()
    data['events_to_send'].append(message)
    await state.update_data(events_to_send=data['events_to_send'])
