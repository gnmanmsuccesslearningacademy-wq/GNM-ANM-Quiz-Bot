from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.database.models import add_user

router = Router()


@router.message(CommandStart())
async def start_cmd(message: Message):

    await add_user(
        message.from_user.id,
        message.from_user.full_name,
        message.from_user.username
    )

    await message.answer(
        f"""
🎉 Welcome {message.from_user.full_name}

GNM / ANM Success Learning Academy

✅ Registration Successful

নিচের Menu থেকে একটি অপশন নির্বাচন করুন।
"""
    )