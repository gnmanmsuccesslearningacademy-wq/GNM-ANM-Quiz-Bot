import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.handlers.start import router as start_router
from app.handlers.user import router as user_router
from app.handlers.leaderboard import router as leaderboard_router
from app.handlers.practice import router as practice_router
from app.handlers.live_exam import router as live_exam_router
from app.handlers.admin_dashboard import router as admin_dashboard_router
from app.handlers.notice import router as notice_router
from app.handlers.external import router as external_router
from config import BOT_TOKEN
from app.database.models import create_tables
from app.handlers.contact import router as contact_router
from app.handlers.admin import router as admin_router
from app.handlers.upload import router as upload_router
from app.handlers.quiz import router as quiz_router

bot = Bot(BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

dp.include_router(start_router)
dp.include_router(contact_router)
dp.include_router(user_router)
dp.include_router(leaderboard_router)
dp.include_router(practice_router)
dp.include_router(live_exam_router)
dp.include_router(admin_dashboard_router)
dp.include_router(notice_router)
dp.include_router(external_router)
dp.include_router(admin_router)
dp.include_router(upload_router)
dp.include_router(quiz_router)
async def main():

    await create_tables()

    print("====================================")
    print("   GNM ANM QUIZ BOT STARTED")
    print("====================================")
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())