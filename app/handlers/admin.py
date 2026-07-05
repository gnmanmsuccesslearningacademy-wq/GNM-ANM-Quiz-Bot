from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from config import ADMIN_ID
from app.states.upload_state import UploadQuestions
from app.states.schedule_state import QuizScheduleStates
from app.database.models import add_quiz_schedule

router = Router()


@router.message(Command("admin"))
async def admin_panel(message: Message, state: FSMContext):
    """Admin panel - Upload Questions"""
    
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Access Denied! Only admin can access this panel.")
        return
    
    text = """👨‍💼 **ADMIN PANEL**

What do you want to do?
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = [
        [InlineKeyboardButton(text="📤 Upload Questions", callback_data="adm_upload")],
        [InlineKeyboardButton(text="📅 Schedule Quiz", callback_data="adm_schedule")],
        [InlineKeyboardButton(text="Back", callback_data="adm_back")]
    ]
    
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "adm_upload")
async def admin_upload_questions(callback_query, state: FSMContext):
    """Handle question upload"""
    
    await state.clear()
    await state.set_state(UploadQuestions.waiting_for_exam)
    
    await callback_query.message.edit_text(
        "📝 Exam Name লিখুন।\n\n"
        "উদাহরণ:\n"
        "GNM ANM 2027"
    )
    await callback_query.answer()


@router.callback_query(F.data == "adm_schedule")
async def admin_schedule_quiz(callback_query, state: FSMContext):
    """Start quiz scheduling process"""
    
    await state.clear()
    await state.set_state(QuizScheduleStates.waiting_for_name)
    
    await callback_query.message.edit_text(
        """📅 **SCHEDULE NEW QUIZ**

Step 1/6: Quiz Name
উদাহরণ: Daily Quiz #25
"""
    )
    await callback_query.answer()


@router.message(QuizScheduleStates.waiting_for_name)
async def schedule_quiz_name(message: Message, state: FSMContext):
    """Get quiz name"""
    
    await state.update_data(quiz_name=message.text)
    await state.set_state(QuizScheduleStates.waiting_for_exam)
    
    await message.answer(
        """Step 2/6: Exam Name
উদাহরণ: GNM ANM 2027"""
    )


@router.message(QuizScheduleStates.waiting_for_exam)
async def schedule_quiz_exam(message: Message, state: FSMContext):
    """Get exam name"""
    
    await state.update_data(exam=message.text)
    await state.set_state(QuizScheduleStates.waiting_for_date)
    
    await message.answer(
        """Step 3/6: Date
Format: YYYY-MM-DD
উদাহরণ: 2026-07-10"""
    )


@router.message(QuizScheduleStates.waiting_for_date)
async def schedule_quiz_date(message: Message, state: FSMContext):
    """Get date"""
    
    date_text = message.text.strip()
    
    # Validate date format
    try:
        from datetime import datetime
        datetime.strptime(date_text, "%Y-%m-%d")
    except ValueError:
        await message.answer("❌ Invalid date! Use format: YYYY-MM-DD")
        return
    
    await state.update_data(date=date_text)
    await state.set_state(QuizScheduleStates.waiting_for_time)
    
    await message.answer(
        """Step 4/6: Time
Format: HH:MM (24-hour)
উদাহরণ: 20:00"""
    )


@router.message(QuizScheduleStates.waiting_for_time)
async def schedule_quiz_time(message: Message, state: FSMContext):
    """Get time"""
    
    time_text = message.text.strip()
    
    # Validate time format
    try:
        from datetime import datetime
        datetime.strptime(time_text, "%H:%M")
    except ValueError:
        await message.answer("❌ Invalid time! Use format: HH:MM (24-hour)")
        return
    
    await state.update_data(time=time_text)
    await state.set_state(QuizScheduleStates.waiting_for_duration)
    
    await message.answer(
        """Step 5/6: Duration (in minutes)
উদাহরণ: 20"""
    )


@router.message(QuizScheduleStates.waiting_for_duration)
async def schedule_quiz_duration(message: Message, state: FSMContext):
    """Get duration"""
    
    try:
        duration = int(message.text.strip())
        if duration <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Invalid duration! Please enter a positive number.")
        return
    
    await state.update_data(duration=duration)
    await state.set_state(QuizScheduleStates.waiting_for_questions)
    
    await message.answer(
        """Step 6/6: Number of Questions
উদাহরণ: 20"""
    )


@router.message(QuizScheduleStates.waiting_for_questions)
async def schedule_quiz_save(message: Message, state: FSMContext):
    """Save quiz schedule to database"""
    
    try:
        question_limit = int(message.text.strip())
        if question_limit <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Invalid number! Please enter a positive number.")
        return
    
    data = await state.get_data()
    
    # Save to database
    quiz_id = await add_quiz_schedule(
        quiz_name=data['quiz_name'],
        exam=data['exam'],
        date=data['date'],
        time=data['time'],
        duration=data['duration'],
        question_limit=question_limit,
        created_by=message.from_user.id
    )
    
    await state.clear()
    
    text = f"""✅ **QUIZ SCHEDULED SUCCESSFULLY**

📝 Quiz: {data['quiz_name']}
📘 Exam: {data['exam']}
📅 Date: {data['date']}
⏰ Time: {data['time']}
⏱️ Duration: {data['duration']} minutes
📊 Questions: {question_limit}
🆔 Quiz ID: {quiz_id}

Bot will automatically announce in the group at the scheduled time.
"""
    
    await message.answer(text)


@router.callback_query(F.data == "adm_back")
async def admin_back(callback_query):
    """Go back"""
    
    await callback_query.message.delete()
    await callback_query.answer()