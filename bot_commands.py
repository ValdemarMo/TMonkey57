import requests
import string
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import BotCommand, Chat
from aiogram.enums import ParseMode
from aiogram.filters import Command
from parser import get_og_data, load_keywords, save_keywords, load_groups, save_groups, start_monitoring, stop_monitoring, check_monitoring, remove_url_numbers
from user_utils import load_users, save_users
from config import OWNER_ID, TELEGRAM_BOT_TOKEN
import re

pending_clear_confirmations = {}


async def setup_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Начать"),
        BotCommand(command="/help", description="Помощь"),
        BotCommand(command="/add_keyword", description="Добавить ключевое слово"),
        BotCommand(command="/remove_keyword", description="Удалить ключевое слово"),
        BotCommand(command="/list_keywords", description="Показать список ключевых слов"),
        BotCommand(command="/add_group", description="Добавить группу"),
        BotCommand(command="/remove_group", description="Удалить группу"),
        BotCommand(command="/list_groups", description="Показать список групп"),
        BotCommand(command="/start_monitoring", description="Начать слежение"),
        BotCommand(command="/stop_monitoring", description="Завершить слежение"),
        BotCommand(command="/check_monitoring", description="Проверить состояние слежения"),
        BotCommand(command="/clear_keywords", description="Очистить список ключевых слов"),
        BotCommand(command="/clear_groups", description="Очистить список групп"),
        BotCommand(command="/add_user", description="Добавить пользователя \n(только для администратора)"),
        BotCommand(command="/remove_user", description="Удалить пользователя \n(только для администратора)"),
        BotCommand(command="/clear_users", description="Очистить список пользователей \n(только для администратора)"),
        BotCommand(command="/list_users", description="Показать список пользователей \n(только для администратора)"),
        BotCommand(command="/send_user_id", description="Показать мой user id (telegramm)")
    ]
    await bot.set_my_commands(commands)
    logging.info("Bot commands have been set")

def register_handlers(dp: Dispatcher, bot: Bot):
    dp.message.register(send_welcome, Command(commands=["start"]))
    dp.message.register(send_help, Command(commands=["help"]))
    dp.message.register(add_keyword, Command(commands=["add_keyword"]))
    dp.message.register(remove_keyword, Command(commands=["remove_keyword"]))
    dp.message.register(list_keywords, Command(commands=["list_keywords"]))
    dp.message.register(add_group, Command(commands=["add_group"]))
    dp.message.register(remove_group, Command(commands=["remove_group"]))
    dp.message.register(list_groups, Command(commands=["list_groups"]))
    dp.message.register(start_monitoring_command, Command(commands=["start_monitoring"]))
    dp.message.register(stop_monitoring_command, Command(commands=["stop_monitoring"]))
    dp.message.register(check_monitoring_command, Command(commands=["check_monitoring"]))
    dp.message.register(clear_keywords, Command(commands=["clear_keywords"]))
    dp.message.register(clear_groups, Command(commands=["clear_groups"]))
    dp.message.register(add_user, Command(commands=["add_user"]))
    dp.message.register(remove_user, Command(commands=["remove_user"]))
    dp.message.register(clear_users, Command(commands=["clear_users"]))
    dp.message.register(list_users, Command(commands=["list_users"]))
    dp.message.register(send_user_id, Command(commands=["send_user_id"]))
    dp.message.register(handle_all_messages)
    logging.info("Handlers have been registered")

def user_is_authorized(user_id):
    users = load_users()
    is_authorized = user_id in users or user_id == OWNER_ID
    logging.info(f"User {user_id} authorization check: {is_authorized}")
    return is_authorized

async def send_user_id(message: types.Message):
    user_id = message.from_user.id
    await message.answer(f"Ваш user id: <b>{user_id}</b>", parse_mode=ParseMode.HTML)

async def get_user_name(user_id: int):
    async with Bot(token=TELEGRAM_BOT_TOKEN) as bot:
        try:
            user: Chat = await bot.get_chat(user_id)
            user_name = user.username if user.username else f"{user.first_name} {user.last_name}"
            user_url = f"https://t.me/{user.username}" if user.username else f"https://t.me/user?id={user_id}"
            return user_name, user_url
        except Exception as e:
            print(f"Failed to get user information for user_id {user_id}: {e}")
            return None, None

async def notify_all_users(bot: Bot, message: str):
    users = load_users()
    for user_id in users:
        await bot.send_message(user_id, message, disable_web_page_preview=True,
                               parse_mode=ParseMode.HTML)
        # try:
        #     await bot.send_message(user_id, message, disable_web_page_preview = True,
        #                            parse_mode=ParseMode.HTML)
        # except Exception as e:
        #     logging.error(f"Failed to send message to {user_id}: {e}")


async def send_welcome(message: types.Message):
    welcome_message = (
        '<b>Добро пожаловать!</b>\n'
        'Для слежения за новой группой:\n'
        '<b>добавьте ключевые слова</b> /add_keyword ***\n'
        '(вставьте слова и фразы через запятую)\n'
        '<b>добавьте группу</b> /add_group *****\n'
        '(вставьте ссылку на запись в группе с которой начнется поиск)\n'
        'нажмите <b>Начать слежение</b> /start_monitoring\n'
        'Используйте /help для просмотра всех доступных команд.'
    )
    await message.answer(welcome_message, parse_mode=ParseMode.HTML)

async def send_help(message: types.Message):
    help_text = (
        "/add_keyword - Добавить ключевое слово\n"
        "/remove_keyword - Удалить ключевое слово\n"
        "/list_keywords - Показать список ключевых слов\n"
        "/add_group - Добавить группу\n"
        "/remove_group - Удалить группу\n"
        "/list_groups - Показать список групп\n"
        "/start_monitoring - Начать слежение\n"
        "/stop_monitoring - Завершить слежение\n"
        "/check_monitoring - Проверка слежения\n"
        "/clear_keywords - Очистить список ключевых слов\n"
        "/clear_groups - Очистить список групп\n"
        # "/add_user - Добавить пользователя\n(только для администратора)\n"
        # "/remove_user - Удалить пользователя\n(только для администратора)\n"
        # "/clear_users - Очистить список пользователей\n(только для администратора)\n"
        # "/list_users - Показать список пользователей\n(только для администратора)\n"
        "/send_user_id - Показать мой user id (telegramm)\n"
    )
    await message.answer(help_text)

async def add_keyword(message: types.Message):
    if not user_is_authorized(message.from_user.id):
        await message.answer("У вас нет прав на выполнение этой команды.")
        return
    if message.text == '/add_keyword':
        await message.answer(f"<b>вы не ввели ключевые слова</b> \n(списком через запятую), попробуйте ещё раз",
                             parse_mode=ParseMode.HTML)
        return
    keywords = load_keywords()
    new_keywords_text = message.text.split(maxsplit=1)[1]
    new_keywords = [kw.strip().replace('_', ' ').translate(str.maketrans('', '', string.punctuation)) for kw in new_keywords_text.split(',')]
    keywords.extend(new_keywords)
    save_keywords(keywords)
    await notify_all_users(message.bot, f"<b>Добавлены ключевые слова:</b>\n" + "\n".join(new_keywords))

async def remove_keyword(message: types.Message):
    if not user_is_authorized(message.from_user.id):
        await message.answer("У вас нет прав на выполнение этой команды.")
        return
    if message.text == '/remove_keyword':
        await message.answer(f"<b>вы не ввели ключевые слова</b> \n(списком через запятую), попробуйте ещё раз",
                             parse_mode=ParseMode.HTML)
        return
    keywords = load_keywords()
    remove_keywords_text = message.text.split(maxsplit=1)[1]
    remove_keywords = [kw.strip().replace('_', ' ').translate(str.maketrans('', '', string.punctuation)) for kw in remove_keywords_text.split(',')]
    keywords = [kw for kw in keywords if kw not in remove_keywords]
    save_keywords(keywords)
    await notify_all_users(message.bot, f"<b>Удалены ключевые слова:</b>\n" + "\n".join(remove_keywords))


async def remove_group(message: types.Message):
    if not user_is_authorized(message.from_user.id):
        await message.answer("У вас нет прав на выполнение этой команды.")
        return

    # Если текст команды только /remove_group, сообщить пользователю
    if message.text.strip() == '/remove_group':
        await message.answer(
            "<b>Вы не ввели название группы</b>, \n(можно скопировать из /list_groups) \nпопробуйте ещё раз",
            parse_mode=ParseMode.HTML)
        return

    # Получить текст после команды /remove_group
    remove_group_name = message.text[len('/remove_group'):].strip()

    # Загружаем существующие группы
    groups = load_groups()

    # Фильтруем группы, чтобы удалить указанную
    updated_groups = [group for group in groups if group["name"] != remove_group_name]

    # Сохраняем обновленный список групп
    save_groups(updated_groups)

    # Отправляем уведомление всем пользователям
    await notify_all_users(message.bot, f"<b>Удалены группы:</b>\n{remove_group_name}", parse_mode=ParseMode.HTML)


async def list_keywords(message: types.Message):
    if not user_is_authorized(message.from_user.id):
        await message.answer("У вас нет прав на выполнение этой команды.")
        return

    keywords = load_keywords()
    await message.answer(f"<b>Ключевые слова:</b>\n" + "\n".join(keywords),
                         parse_mode=ParseMode.HTML)

async def add_group(message: types.Message):
    if not user_is_authorized(message.from_user.id):
        await message.answer("У вас нет прав на выполнение этой команды.")
        return

    if message.text == '/add_group':
        await message.answer("<b>вы не ввели ссылку на сообщение в группе</b>, \nпопробуйте ещё раз",
                         parse_mode=ParseMode.HTML)
        return

    url = message.text.split()[1]
    # post_number = int(url.rstrip('/').rsplit('/', 1)[-1]) + 1000
    # end_url = f"{url.rstrip('/').rsplit('/', 1)[0]}/"
    end_url = f"{remove_url_numbers(url)}/"


    try:
        response = requests.get(end_url)
        response.raise_for_status()
        content = response.text

        og_title, og_description = get_og_data(content)

        new_group = {
            "url": url,
            "name": og_title,
            "end_key": og_description
        }

        groups = load_groups()
        for i, group in enumerate(groups):
            if group['name'] == og_title:
                groups[i] = new_group
                break
        else:
            groups.append(new_group)

        save_groups(groups)

        await notify_all_users(message.bot, f"<b>Добавлена группа:</b> \n{og_title}")
    except requests.RequestException as e:
        await message.answer(f"Ошибка при добавлении группы: {e}")


async def list_groups(message: types.Message):
    if not user_is_authorized(message.from_user.id):
        await message.answer("У вас нет прав на выполнение этой команды.")
        return

    groups = load_groups()
    group_names  = [f'<a href="{remove_url_numbers(group["url"])}">{group["name"]}</a>' for group in groups]
    await message.answer(f"<b>Группы:</b>\n" + "\n".join(group_names ),
                         disable_web_page_preview=True, parse_mode=ParseMode.HTML)


async def start_monitoring_command(message: types.Message):
    if not user_is_authorized(message.from_user.id):
        await message.answer("У вас нет прав на выполнение этой команды.")
        return

    await message.answer("Запуск слежения...")
    await start_monitoring(lambda msg: notify_all_users(message.bot, msg))

async def stop_monitoring_command(message: types.Message):
    if not user_is_authorized(message.from_user.id):
        await message.answer("У вас нет прав на выполнение этой команды.")
        return

    await message.answer("Остановка слежения...")
    stop_monitoring()
async def check_monitoring_command(message: types.Message):
    if not user_is_authorized(message.from_user.id):
        await message.answer("У вас нет прав на выполнение этой команды.")
        return

    await message.answer(check_monitoring())

async def clear_keywords(message: types.Message):
    if not user_is_authorized(message.from_user.id):
        await message.answer("У вас нет прав на выполнение этой команды.")
        return

    pending_clear_confirmations[message.from_user.id] = "clear_keywords"
    await message.answer("Вы уверены, что <b>хотите очистить список ключевых слов?</b> Ответьте <b>'подтвердить очистку'</b> для подтверждения.",
                         parse_mode=ParseMode.HTML)

async def clear_groups(message: types.Message):
    if not user_is_authorized(message.from_user.id):
        await message.answer("У вас нет прав на выполнение этой команды.")
        return

    pending_clear_confirmations[message.from_user.id] = "clear_groups"
    await message.answer("Вы уверены, что хотите очистить список групп? Ответьте <b>'подтвердить очистку'</b> для подтверждения.",
                         parse_mode=ParseMode.HTML)

async def add_user(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("У вас нет прав на выполнение этой команды.")
        return

    if message.text == '/add_user':
        await message.answer("<b>вы не ввели Telegramm user ID</b>, \nпопробуйте ещё раз",
                         parse_mode=ParseMode.HTML)
        return
    new_user_id = int(message.text.split()[1])
    users = load_users()
    if new_user_id not in users:
        users.append(new_user_id)
        save_users(users)
        await message.answer(f"Пользователь <b>{new_user_id}</b> добавлен.",
                         parse_mode=ParseMode.HTML)
    else:
        await message.answer(f"Пользователь <b>{new_user_id}</b> уже существует.",
                         parse_mode=ParseMode.HTML)

async def remove_user(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("У вас нет прав на выполнение этой команды.")
        return

    if message.text == '/remove_user':
        await message.answer("<b>вы не ввели Telegramm user ID</b>, \nпопробуйте ещё раз",
                         parse_mode=ParseMode.HTML)
        return
    user_id_to_remove = int(message.text.split()[1])
    users = load_users()
    if user_id_to_remove in users:
        users.remove(user_id_to_remove)
        save_users(users)
        await message.answer(f"Пользователь <b>{user_id_to_remove}</b> удален.",
                             parse_mode=ParseMode.HTML)
    else:
        await message.answer(f"Пользователь <b>{user_id_to_remove}</b> не найден.",
                             parse_mode=ParseMode.HTML)

async def clear_users(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("У вас нет прав на выполнение этой команды.")
        return

    pending_clear_confirmations[message.from_user.id] = "clear_users"
    await message.answer("Вы уверены, что <b>хотите удалить всех пользователей?</b> Ответьте <b>'подтвердить очистку'</b> для подтверждения.",
                         parse_mode=ParseMode.HTML)

# async def list_users(message: types.Message):
#     if message.from_user.id != OWNER_ID:
#         await message.answer("У вас нет прав на выполнение этой команды.")
#         return
#
#     users = load_users()
#     await message.answer(f"<b>Пользователи:</b>\n" + "\n".join(map(str, users)),
#                          parse_mode=ParseMode.HTML)

async def list_users(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("У вас нет прав на выполнение этой команды.")
        return

    users = load_users()
    user_list = []
    invalid_users = []

    for user_id in users:
        user_name, user_url = await get_user_name(user_id)
        if user_name and user_url:
            user_list.append(f'{user_id} - <a href="{user_url}">{user_name}</a>')
        else:
            user_list.append(f'User ID: {user_id} (name not found)')
            invalid_users.append(user_id)

    # Удалить недействительных пользователей из списка
    if invalid_users:
        users = [user_id for user_id in users if user_id not in invalid_users]
        save_users(users)

    await message.answer(f"<b>Пользователи:</b>\n" + "\n".join(user_list), disable_web_page_preview=True,
                               parse_mode=ParseMode.HTML)

async def handle_all_messages(message: types.Message):
    if message.from_user.id not in pending_clear_confirmations:
        await message.answer("У вас нет прав на выполнение этой команды.")
        return

    if message.text.lower() == "подтвердить очистку":
        confirmation = pending_clear_confirmations.pop(message.from_user.id, None)
        if confirmation == "clear_users":
            users = [OWNER_ID]
            save_users(users)
            await message.answer("Список пользователей очищен. Остался только администратор.")
        elif confirmation == "clear_keywords":
            keywords = []
            save_keywords(keywords)
            await notify_all_users(message.bot, "Список ключевых слов очищен.")
        elif confirmation == "clear_groups":
            groups = []
            save_groups(groups)
            await notify_all_users(message.bot, "Список групп очищен.")
        else:
            await message.answer("Нет ожидающих подтверждений для выполнения.")
    else:
        await message.answer("Неверная команда. Используйте /help для просмотра доступных команд.")

