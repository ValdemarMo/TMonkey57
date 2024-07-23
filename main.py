import asyncio
from aiogram import Bot, Dispatcher
from bot_commands import register_handlers, setup_bot_commands
from config import TELEGRAM_BOT_TOKEN, OWNER_ID
from user_utils import load_users, save_users


async def main():

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()

    users = load_users()
    if OWNER_ID not in users:
        users.append(OWNER_ID)
        save_users(users)

    await setup_bot_commands(bot)
    register_handlers(dp, bot)

    logging.info("Starting bot")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    import logging

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    asyncio.run(main())

# import asyncio
# from aiogram import Bot, Dispatcher
# from aiogram.fsm.storage.memory import MemoryStorage
# from bot_commands import register_handlers, setup_bot_commands
# from config import TELEGRAM_BOT_TOKEN
#
# async def main():
#     bot = Bot(token=TELEGRAM_BOT_TOKEN)
#     dp = Dispatcher(storage=MemoryStorage())
#
#     await setup_bot_commands(bot)
#     register_handlers(dp, bot)
#
#     await dp.start_polling(bot)
#
# if __name__ == "__main__":
#     asyncio.run(main())
