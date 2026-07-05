from aiogram import Router, F
from aiogram.types import Message

from app.keyboards.main_menu import get_main_menu

router = Router()


@router.message(F.text == "📢 Notice")
async def show_notices(message: Message):
    """Show notices"""
    
    text = """📢 **NOTICES**

📌 Latest Updates:

1. **🎉 New Exam System Live**
   - Live quizzes with real-time ranking
   - Pause and resume feature available
   
2. **📚 Subject Updates**
   - Anatomy chapter updated
   - 50 new questions added
   
3. **🏆 Leaderboard Competition**
   - Weekly prizes for top 3
   - Next reset: Sunday 00:00

4. **⚠️ Important**
   - Server maintenance on Tuesday
   - Expected downtime: 2 hours

---

📋 Show older notices?
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = [
        [InlineKeyboardButton(text="📖 Show All", callback_data="notice_all")],
        [InlineKeyboardButton(text="Back", callback_data="notice_back")]
    ]
    
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "notice_all")
async def show_all_notices(callback_query):
    """Show all notices"""
    
    text = """📋 **ALL NOTICES**

📌 Latest:
- New exam system launched
- 50 new anatomy questions added

📌 Last Week:
- Performance improvement
- Bug fixes

📌 Older:
- Welcome to GNM/ANM Quiz Bot
- Initial launch
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = [[InlineKeyboardButton(text="Back", callback_data="notice_back")]]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=kb)
    await callback_query.answer()


@router.callback_query(F.data == "notice_back")
async def notice_back(callback_query):
    """Back to main"""
    await callback_query.message.delete()
    await callback_query.answer()
