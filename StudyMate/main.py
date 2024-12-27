import asyncio
from aiogram import Bot, Dispatcher
from app.handlers import router
from app.db import Database

async def main():
    db = Database(path="Study_bot.db")
    await db.create_users_table()
    await db.create_tasks_table()
    bot = Bot(token='7868329061:AAHSllSP90q4F1t_W9ljPVLPdAu8S009_qM')
    
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')