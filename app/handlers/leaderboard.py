from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.database.models import get_leaderboard
from app.keyboards.main_menu import get_main_menu
from app.utils.helpers import format_leaderboard

router = Router()


@router.message(F.text == "🏆 Leaderboard")
async def show_leaderboard(message: Message, state: FSMContext):
    """Show leaderboard options"""
    
    text = """🏆 **LEADERBOARD**

Choose ranking type:
"""
    
    keyboard_data = [
        ("Daily Top 10", "lb_daily"),
        ("Weekly Top 10", "lb_weekly"),
        ("Monthly Top 10", "lb_monthly"),
        ("All Time Top 10", "lb_alltime"),
        ("Subject Wise", "lb_subject"),
        ("Back", "lb_back")
    ]
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = []
    for label, callback in keyboard_data:
        buttons.append([InlineKeyboardButton(text=label, callback_data=callback)])
    
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "lb_alltime")
async def leaderboard_alltime(callback_query):
    """Show all-time leaderboard"""
    
    leaderboard = await get_leaderboard("all_time", limit=10)
    text = format_leaderboard(leaderboard)
    
    await callback_query.message.edit_text(text)
    await callback_query.answer()


@router.callback_query(F.data == "lb_daily")
async def leaderboard_daily(callback_query):
    """Show daily leaderboard"""
    
    leaderboard = await get_leaderboard("daily", limit=10)
    text = "📅 **DAILY LEADERBOARD**\n\n"
    
    if not leaderboard:
        text += "No data available for today"
    else:
        text += format_leaderboard(leaderboard)
    
    await callback_query.message.edit_text(text)
    await callback_query.answer()


@router.callback_query(F.data == "lb_weekly")
async def leaderboard_weekly(callback_query):
    """Show weekly leaderboard"""
    
    leaderboard = await get_leaderboard("weekly", limit=10)
    text = "📆 **WEEKLY LEADERBOARD**\n\n"
    
    if not leaderboard:
        text += "No data available this week"
    else:
        text += format_leaderboard(leaderboard)
    
    await callback_query.message.edit_text(text)
    await callback_query.answer()


@router.callback_query(F.data == "lb_monthly")
async def leaderboard_monthly(callback_query):
    """Show monthly leaderboard"""
    
    leaderboard = await get_leaderboard("monthly", limit=10)
    text = "📊 **MONTHLY LEADERBOARD**\n\n"
    
    if not leaderboard:
        text += "No data available this month"
    else:
        text += format_leaderboard(leaderboard)
    
    await callback_query.message.edit_text(text)
    await callback_query.answer()


@router.callback_query(F.data == "lb_subject")
async def leaderboard_subject(callback_query):
    """Show subject-wise leaderboard"""
    
    text = """📚 **SUBJECT WISE RANKING**

Choose a subject:
"""
    
    subjects = [
        ("Anatomy", "lb_sub_anatomy"),
        ("Physiology", "lb_sub_physiology"),
        ("Pathology", "lb_sub_pathology"),
        ("Back", "lb_back")
    ]
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = [[InlineKeyboardButton(text=subj, callback_data=cb)] for subj, cb in subjects]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=kb)
    await callback_query.answer()


@router.callback_query(F.data == "lb_back")
async def leaderboard_back(callback_query):
    """Go back to main leaderboard menu"""
    
    await callback_query.message.delete()
    await callback_query.answer()
