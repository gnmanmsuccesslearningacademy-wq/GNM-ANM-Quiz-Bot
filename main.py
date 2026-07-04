import asyncio

from aiogram import Bot, Dispatcher
from app.handlers.start import router as start_router
from config import BOT_TOKEN
from app.database.models import create_tables
from app.handlers.contact import router as contact_router
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# dp.include_router(start_router)
dp.include_router(contact_router)
async def main():

    await create_tables()

    print("====================================")
    print("   GNM ANM QUIZ BOT STARTED")
    print("====================================")
    dp.include_router(start_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())