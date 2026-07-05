from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.database.models import update_phone
from app.keyboards.main_menu import get_main_menu

router = Router()


class PhoneStates(StatesGroup):
    waiting_for_phone = State()


@router.message(F.text == "📞 Contact")
async def show_contact_options(message: Message):
    """Show contact options"""
    
    text = """📞 **CONTACT US**

Choose how to provide your contact:
"""
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Share Contact", request_contact=True)],
            [KeyboardButton(text="✏️ Manual Entry")],
            [KeyboardButton(text="Back")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(text, reply_markup=keyboard)


@router.message(lambda message: message.contact is not None)
async def save_contact(message: Message, state: FSMContext):

    phone = message.contact.phone_number

    await update_phone(
        message.from_user.id,
        phone
    )

    await state.clear()

    await message.answer(
        "✅ আপনার মোবাইল নম্বর সফলভাবে সংরক্ষণ করা হয়েছে।",
        reply_markup=get_main_menu()
    )


@router.message(F.text == "Manual Entry")
async def manual_phone_entry(message: Message, state: FSMContext):
    
    await state.set_state(PhoneStates.waiting_for_phone)
    
    await message.answer(
        "📱 আপনার 10-digit মোবাইল নম্বর লিখুন (যেমন: 9876543210)"
    )


@router.message(PhoneStates.waiting_for_phone)
async def save_manual_phone(message: Message, state: FSMContext):
    
    phone = message.text.strip()
    
    if not phone.isdigit() or len(phone) < 10:
        await message.answer(
            "❌ Invalid phone number! Please enter a valid 10-digit number."
        )
        return
    
    await state.clear()
    
    await update_phone(
        message.from_user.id,
        phone
    )

    await message.answer(
        "✅ আপনার মোবাইল নম্বর সফলভাবে সংরক্ষণ করা হয়েছে।",
        reply_markup=get_main_menu()
    )


@router.message(F.text == "Back")
async def go_back(message: Message):
    """Go back to main menu"""
    
    from app.keyboards.main_menu import get_main_menu
    await message.answer("Back to main menu", reply_markup=get_main_menu())