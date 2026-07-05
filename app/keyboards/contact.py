from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_contact_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Share Contact", request_contact=True)],
            [KeyboardButton(text="Manual Entry")]
        ],
        resize_keyboard=True
    )