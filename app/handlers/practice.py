from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.database.models import get_random_question
from app.keyboards.main_menu import get_main_menu
from app.keyboards.quiz_keyboard import quiz_keyboard

router = Router()


class PracticeQuizStates(StatesGroup):
    choosing_type = State()
    choosing_subject = State()
    choosing_chapter = State()
    choosing_difficulty = State()
    quiz_active = State()


@router.message(F.text == "📚 Practice")
async def start_practice_quiz(message: Message, state: FSMContext):
    """Show practice quiz options"""
    
    text = """📚 **PRACTICE QUIZ**

Choose quiz type:
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = [
        [InlineKeyboardButton(text="📖 Subject Wise", callback_data="pq_subject")],
        [InlineKeyboardButton(text="📕 Chapter Wise", callback_data="pq_chapter")],
        [InlineKeyboardButton(text="⭐ Difficulty Wise", callback_data="pq_difficulty")],
        [InlineKeyboardButton(text="🎲 Random Practice", callback_data="pq_random")],
        [InlineKeyboardButton(text="Back", callback_data="pq_back")]
    ]
    
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "pq_subject")
async def choose_subject(callback_query: CallbackQuery, state: FSMContext):
    """Show available subjects"""
    
    text = """📖 **SELECT SUBJECT**

"""
    
    subjects = [
        ("Anatomy", "pqs_anatomy"),
        ("Physiology", "pqs_physiology"),
        ("Pathology", "pqs_pathology"),
        ("Back", "pq_back")
    ]
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = [[InlineKeyboardButton(text=s, callback_data=cb)] for s, cb in subjects]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=kb)
    await callback_query.answer()


@router.callback_query(F.data == "pq_chapter")
async def choose_chapter(callback_query: CallbackQuery, state: FSMContext):
    """Show chapter selection"""
    
    text = """📕 **SELECT CHAPTER**

"""
    
    chapters = [
        ("Chapter 1", "pqc_ch1"),
        ("Chapter 2", "pqc_ch2"),
        ("Chapter 3", "pqc_ch3"),
        ("Back", "pq_back")
    ]
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = [[InlineKeyboardButton(text=c, callback_data=cb)] for c, cb in chapters]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=kb)
    await callback_query.answer()


@router.callback_query(F.data == "pq_difficulty")
async def choose_difficulty(callback_query: CallbackQuery, state: FSMContext):
    """Show difficulty options"""
    
    text = """⭐ **SELECT DIFFICULTY**

"""
    
    difficulties = [
        ("🟢 Easy", "pqd_easy"),
        ("🟡 Medium", "pqd_medium"),
        ("🔴 Hard", "pqd_hard"),
        ("🌈 Mixed", "pqd_mixed"),
        ("Back", "pq_back")
    ]
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = [[InlineKeyboardButton(text=d, callback_data=cb)] for d, cb in difficulties]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=kb)
    await callback_query.answer()


@router.callback_query(F.data == "pq_random")
async def random_practice_quiz(callback_query: CallbackQuery, state: FSMContext):
    """Start random practice quiz"""
    
    question = await get_random_question()
    
    if not question:
        await callback_query.answer("❌ No questions available", show_alert=True)
        return
    
    await state.set_state(PracticeQuizStates.quiz_active)
    
    text = f"""
🎯 **PRACTICE QUIZ - Random**

📚 Subject: {question[2]}
📖 Chapter: {question[3]}

❓ {question[4]}

🅰️ {question[5]}
🅱️ {question[6]}
🇨 {question[7]}
🇩 {question[8]}
"""
    
    await callback_query.message.edit_text(text, reply_markup=quiz_keyboard(question[0]))
    await callback_query.answer()


@router.callback_query(F.data == "pq_back")
async def practice_back(callback_query: CallbackQuery, state: FSMContext):
    """Go back to main menu"""
    
    await callback_query.message.delete()
    await callback_query.answer()
