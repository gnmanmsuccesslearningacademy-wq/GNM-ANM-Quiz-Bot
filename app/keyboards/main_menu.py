from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu():
    """Simple main menu - only essential features"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Live Quiz")],
            [
                KeyboardButton(text="🏆 Leaderboard"),
                KeyboardButton(text="📊 My Result")
            ],
            [
                KeyboardButton(text="👤 My Profile"),
                KeyboardButton(text="📞 Contact")
            ]
        ],
        resize_keyboard=True
    )


# Default export
main_menu = get_main_menu()