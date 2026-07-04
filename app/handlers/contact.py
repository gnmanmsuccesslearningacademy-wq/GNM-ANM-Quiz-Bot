from aiogram import Router
from aiogram.types import Message

from app.database.models import update_phone
from app.keyboards.main_menu import main_menu

router = Router()


@router.message(lambda message: message.contact is not None)
async def save_contact(message: Message):

    phone = message.contact.phone_number

    await update_phone(
        message.from_user.id,
        phone
    )

    await message.answer(
        "✅ আপনার মোবাইল নম্বর সফলভাবে সংরক্ষণ করা হয়েছে।",
        reply_markup=main_menu
    )