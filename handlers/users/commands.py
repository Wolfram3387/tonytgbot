from aiogram import types
from utils.misc import rate_limit
from filters import IsPrivate, IsNotAdmin
from sqlalchemy.exc import IntegrityError
from aiogram.dispatcher import FSMContext
from loader import dp, users_db, variants_db
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.builtin import CommandHelp, CommandStart

from data.config import admins
from keyboards.default import u_menu, a_menu
from keyboards.default import AdminButtons, UserButtons


# общий handler
@dp.message_handler(Command('state'), IsPrivate(), state='*')
async def test_states(message: types.Message, state: FSMContext):
    """Информирует пользователя или админа о текущем сценарии и FSM данных"""
    state_name = await state.get_state()
    user_data = await state.get_data()
    await message.answer(f'state = {state_name},\ndata = {user_data}')


# ================================================================================================
# ============================================== USERS ===========================================
# ================================================================================================


@rate_limit(5, 'help')
@dp.message_handler(CommandHelp(), IsNotAdmin(), IsPrivate(), state='*')
async def help_for_user(message: types.Message):
    """Команда /help для пользователя"""
    text = [
        'Список команд: ',
        '/start - Начать диалог',
        '/help - Получить справку',
        '/menu - Показать меню',
        '/variants - Показать id вариантов'
    ]
    await message.answer('\n'.join(text))


@dp.message_handler(CommandStart(), IsNotAdmin(), IsPrivate(), state='*')
async def start_for_user(message: types.Message, state: FSMContext):
    """Команда /start для пользователя"""
    with open('command_start.txt') as file:
        await message.answer(file.read().format(name=message.from_user.full_name), reply_markup=u_menu)
    try:
        users_db.add_user(
            user_id=message.from_user.id,
            name=message.from_user.full_name
        )
    except IntegrityError:
        pass


@dp.message_handler(Command('menu'), IsNotAdmin(), IsPrivate(), state='*')
async def show_user_menu(message: types.Message, state: FSMContext):
    """Показывает раскладку меню для пользователя"""
    await state.finish()
    await message.answer(UserButtons.menu, reply_markup=u_menu)


@dp.message_handler(Command('variants'), IsPrivate(), state='*')
async def show_variants(message: types.Message):
    """Показывает все варианты и их id"""
    variants = '\n'.join([f'{line[0]} - {line[1]}' for line in
                          sorted(variants_db.select_all_variants(), key=lambda line: int(line[0]))])
    await message.answer(f'Все варианты:\n{variants}')


@dp.message_handler(Command('whatsnew'), IsPrivate(), state='*')
async def whats_new(message: types.Message):
    """Показывает, что добавилось в текущем обновлении"""
    with open('whats_new.txt', encoding='utf8') as file:
        await message.answer(file.read())


@dp.message_handler(Command('timetable'), IsPrivate(), state='*')
async def timetable(message: types.Message):
    msg = ['Вот твоё расписание на ближайшую неделю:']
    # for day, time, _ in zip(, , range(7)):
    #     msg.append(f'{day}: {time}')

# =================================================================================================
# ============================================== ADMINS ===========================================
# =================================================================================================


@dp.message_handler(CommandHelp(), IsPrivate(), user_id=admins, state='*')
async def help_for_admin(message: types.Message):
    """Команда /help для админа"""
    text = [
        'Список команд для админа: ',
        '/menu - Показать меню',
        '/state - Проверить состояние',
        '/users - Показать id пользователей',
        '/variants - Показать id вариантов',
    ]
    await message.answer('\n'.join(text))


@dp.message_handler(CommandStart(), IsPrivate(), user_id=admins, state='*')
async def start_for_admin(message: types.Message):
    """Команда /start для админа"""
    await message.answer('Зачем админу команда старт?...')


@dp.message_handler(Command('menu'), IsPrivate(), user_id=admins, state='*')
async def show_admin_menu(message: types.Message, state: FSMContext):
    """Показывает раскладку меню для админа"""
    await state.finish()
    await message.answer(AdminButtons.menu, reply_markup=a_menu)


@dp.message_handler(Command('users'), IsPrivate(), user_id=admins, state='*')
async def show_users(message: types.Message):
    """Показывает всех пользователей и их id для админа"""
    users = '\n'.join(['{0:>12} - {1:<}'.format(line[0], line[1]) for line in sorted(
        users_db.select_all_users(), key=lambda line: line[1])])
    await message.answer(f'Текущие пользователи:\n{users}')
