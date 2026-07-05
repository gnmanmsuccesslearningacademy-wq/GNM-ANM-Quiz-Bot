import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.handlers.start import router as start_router
from app.handlers.user import router as user_router
from app.handlers.leaderboard import router as leaderboard_router
from app.handlers.contact import router as contact_router
from app.handlers.admin import router as admin_router
from app.handlers.upload import router as upload_router
from app.scheduler.quiz_scheduler import check_and_announce_quizzes
from config import BOT_TOKEN
from app.database.models import create_tables

bot = Bot(BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

dp.include_router(start_router)  # Must be first for /start command and quiz deep links
dp.include_router(contact_router)
dp.include_router(user_router)
dp.include_router(leaderboard_router)
dp.include_router(admin_router)
dp.include_router(upload_router)


async def main():

    await create_tables()

    print("====================================")
    print("   GNM ANM QUIZ BOT STARTED")
    print("====================================")
    
    # Start scheduler in background
    scheduler_task = asyncio.create_task(check_and_announce_quizzes(bot))
    
    try:
        await dp.start_polling(bot)
    finally:
        scheduler_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())