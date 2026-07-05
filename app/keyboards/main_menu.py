from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📝 Live Quiz"),
                KeyboardButton(text="📚 Practice")
            ],
            [
                KeyboardButton(text="🏆 Leaderboard"),
                KeyboardButton(text="📊 My Result")
            ],
            [
                KeyboardButton(text="👤 My Profile"),
                KeyboardButton(text="📢 Notice")
            ],
            [
                KeyboardButton(text="🎥 YouTube"),
                KeyboardButton(text="💎 Paid Course")
            ]
        ],
        resize_keyboard=True
    )


def get_quiz_type_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Subject Wise"), KeyboardButton(text="Chapter Wise")],
            [KeyboardButton(text="Difficulty Wise"), KeyboardButton(text="Random")],
            [KeyboardButton(text="Back")]
        ],
        resize_keyboard=True
    )


def get_admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Upload Questions"), KeyboardButton(text="Broadcast")],
            [KeyboardButton(text="Statistics"), KeyboardButton(text="Active Users")],
            [KeyboardButton(text="Manage Questions"), KeyboardButton(text="Block User")],
            [KeyboardButton(text="Backup Database"), KeyboardButton(text="Back")]
        ],
        resize_keyboard=True
    )


# Default export
main_menu = get_main_menu()