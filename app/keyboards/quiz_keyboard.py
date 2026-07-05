from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def quiz_keyboard(question_id):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🅰️ A", callback_data=f"answer:A:{question_id}"),
                InlineKeyboardButton(text="🅱️ B", callback_data=f"answer:B:{question_id}")
            ],
            [
                InlineKeyboardButton(text="🇨 C", callback_data=f"answer:C:{question_id}"),
                InlineKeyboardButton(text="🇩 D", callback_data=f"answer:D:{question_id}")
            ]
        ]
    )

    return keyboard