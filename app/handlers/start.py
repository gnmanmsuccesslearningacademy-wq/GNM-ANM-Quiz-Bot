from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.database.models import add_user
from app.keyboards.contact import contact_keyboard

router = Router()


@router.message(CommandStart())
async def start_command(message: Message):
    await add_user(
        message.from_user.id,
        message.from_user.full_name,
        message.from_user.username,
    )

    name = message.from_user.full_name or message.from_user.first_name or "Student"

    await message.answer(
        f"""🎉 Welcome {name}

📚 GNM / ANM Success Learning Academy

📱 প্রথমে আপনার মোবাইল নম্বর Verify করুন।

নিচের "📱 Share Contact" বাটনে চাপুন।""",
        reply_markup=contact_keyboard,
    )