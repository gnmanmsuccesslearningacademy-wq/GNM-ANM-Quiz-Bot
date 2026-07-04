from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
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