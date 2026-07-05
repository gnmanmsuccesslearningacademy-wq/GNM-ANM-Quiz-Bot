from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.database.models import (
    get_user_stats,
    get_quiz_history,
    get_bookmarks
)
from app.keyboards.main_menu import get_main_menu
from app.utils.helpers import format_user_stats, calculate_accuracy

router = Router()


@router.message(F.text == "👤 My Profile")
async def show_profile(message: Message, state: FSMContext):
    """Show user profile and statistics"""
    
    user_id = message.from_user.id
    stats = await get_user_stats(user_id)
    
    if not stats:
        await message.answer(
            "❌ Profile not found. Please use /start first.",
            reply_markup=get_main_menu()
        )
        return
    
    profile_text = format_user_stats(stats)
    
    await message.answer(
        profile_text,
        reply_markup=get_main_menu()
    )


@router.message(F.text == "📊 My Result")
async def show_results(message: Message, state: FSMContext):
    """Show quiz history and results"""
    
    user_id = message.from_user.id
    history = await get_quiz_history(user_id, limit=5)
    
    if not history:
        await message.answer(
            "❌ No quiz history found. Start your first quiz!",
            reply_markup=get_main_menu()
        )
        return
    
    text = "📊 **YOUR QUIZ HISTORY (Last 5)**\n\n"
    
    for idx, (quiz_id, _, score, total_marks, accuracy, quiz_date) in enumerate(history, 1):
        text += f"{idx}. Score: {score}/{total_marks}\n"
        text += f"   Accuracy: {accuracy}%\n"
        text += f"   Date: {quiz_date}\n\n"
    
    await message.answer(
        text,
        reply_markup=get_main_menu()
    )


@router.message(F.text == "📚 Bookmarks")
async def show_bookmarks(message: Message, state: FSMContext):
    """Show bookmarked questions"""
    
    user_id = message.from_user.id
    bookmarks = await get_bookmarks(user_id)
    
    if not bookmarks:
        await message.answer(
            "❌ No bookmarked questions yet!",
            reply_markup=get_main_menu()
        )
        return
    
    text = f"📚 **YOUR BOOKMARKS** ({len(bookmarks)} questions)\n\n"
    
    for idx, question in enumerate(bookmarks[:5], 1):
        q_id, exam, subject, chapter, question_text, *_ = question
        text += f"{idx}. {question_text[:50]}...\n"
        text += f"   Chapter: {chapter}\n\n"
    
    if len(bookmarks) > 5:
        text += f"\n... and {len(bookmarks) - 5} more questions"
    
    await message.answer(
        text,
        reply_markup=get_main_menu()
    )
