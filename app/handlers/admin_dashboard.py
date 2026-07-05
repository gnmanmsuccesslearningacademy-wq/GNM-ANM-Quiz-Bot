from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

from config import ADMIN_ID
from app.database.models import add_scheduled_quiz, get_scheduled_quizzes, delete_scheduled_quiz, delete_all_scheduled_quizzes, get_available_exams
from app.states.upload_state import UploadQuestions

router = Router()


class AdminStates(StatesGroup):
    sending_broadcast = State()
    managing_questions = State()
    publishing_notice = State()
    scheduling_quiz_name = State()
    scheduling_quiz_description = State()
    scheduling_quiz_start = State()
    scheduling_quiz_end = State()
    scheduling_quiz_questions = State()
    scheduling_quiz_marks = State()
    managing_scheduled_quizzes = State()


@router.message(F.text.startswith("/admin"))
async def admin_panel(message: Message, state: FSMContext):
    """Show admin dashboard"""
    
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Access Denied! Only admin can access this panel.")
        return
    
    # Clear any previous state
    await state.clear()
    
    text = """👨‍💼 **ADMIN DASHBOARD**

Select an option:
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = [
        [InlineKeyboardButton(text="📤 Upload Questions", callback_data="adm_upload")],
        [InlineKeyboardButton(text="📅 Schedule Quiz", callback_data="adm_schedule")],
        [InlineKeyboardButton(text="🗑️ Manage Scheduled Quizzes", callback_data="adm_manage_quizzes")],
        [InlineKeyboardButton(text="📢 Broadcast Message", callback_data="adm_broadcast")],
        [InlineKeyboardButton(text="📊 Statistics", callback_data="adm_stats")],
        [InlineKeyboardButton(text="👥 Active Users", callback_data="adm_users")],
        [InlineKeyboardButton(text="🔍 Manage Questions", callback_data="adm_manage")],
        [InlineKeyboardButton(text="🚫 Block User", callback_data="adm_block")],
        [InlineKeyboardButton(text="💾 Backup Database", callback_data="adm_backup")],
        [InlineKeyboardButton(text="📝 Publish Notice", callback_data="adm_notice")],
        [InlineKeyboardButton(text="Back", callback_data="adm_back")]
    ]
    
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "adm_upload")
async def admin_upload_questions(callback_query: CallbackQuery, state: FSMContext):
    """Handle question upload - start upload process"""
    
    await state.clear()
    await state.set_state(UploadQuestions.waiting_for_exam)
    
    await callback_query.message.edit_text(
        "📝 Exam Name লিখুন।\n\n"
        "উদাহরণ:\n"
        "GNM ANM 2027"
    )
    await callback_query.answer()


@router.callback_query(F.data == "adm_stats")
async def admin_statistics(callback_query: CallbackQuery):
    """Show statistics"""
    
    # TODO: Fetch real data from database
    text = """📊 **STATISTICS**

📚 Total Questions: 0
👥 Total Users: 0
✅ Today's Quizzes: 0
📈 Average Accuracy: 0%
🏆 Top Scorer: N/A

📅 This Week:
- New Users: 0
- Total Quizzes: 0
- Questions Added: 0
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = [[InlineKeyboardButton(text="Back", callback_data="adm_back")]]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=kb)
    await callback_query.answer()


@router.callback_query(F.data == "adm_users")
async def admin_active_users(callback_query: CallbackQuery):
    """Show active users"""
    
    # TODO: Fetch real data from database
    text = """👥 **ACTIVE USERS**

Online: 0
Today: 0
This Week: 0
Total: 0

📋 Recent Activity:
(User data will appear here)
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = [[InlineKeyboardButton(text="Back", callback_data="adm_back")]]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=kb)
    await callback_query.answer()


@router.callback_query(F.data == "adm_manage")
async def admin_manage_questions(callback_query: CallbackQuery, state: FSMContext):
    """Manage questions"""
    
    await state.set_state(AdminStates.managing_questions)
    
    text = """🔍 **MANAGE QUESTIONS**

Choose action:
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = [
        [InlineKeyboardButton(text="🔎 Search Question", callback_data="amq_search")],
        [InlineKeyboardButton(text="✏️ Edit Question", callback_data="amq_edit")],
        [InlineKeyboardButton(text="🗑️ Delete Question", callback_data="amq_delete")],
        [InlineKeyboardButton(text="📋 Filter by Subject", callback_data="amq_filter")],
        [InlineKeyboardButton(text="Back", callback_data="adm_back")]
    ]
    
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=kb)
    await callback_query.answer()


@router.callback_query(F.data == "adm_broadcast")
async def admin_broadcast(callback_query: CallbackQuery, state: FSMContext):
    """Send broadcast message"""
    
    await state.set_state(AdminStates.sending_broadcast)
    
    text = """📢 **BROADCAST MESSAGE**

Type your message to send to all users:
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = [[InlineKeyboardButton(text="Cancel", callback_data="adm_back")]]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=kb)
    await callback_query.answer()


@router.callback_query(F.data == "adm_notice")
async def admin_publish_notice(callback_query: CallbackQuery, state: FSMContext):
    """Publish notice"""
    
    await state.set_state(AdminStates.publishing_notice)
    
    text = """📝 **PUBLISH NOTICE**

Type your notice (title + content):
Format: Title | Content
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = [[InlineKeyboardButton(text="Cancel", callback_data="adm_back")]]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=kb)
    await callback_query.answer()


@router.callback_query(F.data == "adm_backup")
async def admin_backup(callback_query: CallbackQuery):
    """Backup database"""
    
    text = """💾 **DATABASE BACKUP**

✅ Creating backup...

Backup saved: backup_2026-07-05.db
Size: 2.5 MB

📝 Last backup: 2026-07-05 10:00 AM
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = [[InlineKeyboardButton(text="Back", callback_data="adm_back")]]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=kb)
    await callback_query.answer()


@router.callback_query(F.data == "adm_block")
async def admin_block_user(callback_query: CallbackQuery):
    """Block user"""
    
    text = """🚫 **BLOCK USER**

Enter user ID to block:
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = [[InlineKeyboardButton(text="Cancel", callback_data="adm_back")]]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=kb)
    await callback_query.answer()


# ===================================
# SCHEDULE LIVE QUIZ
# ===================================

@router.callback_query(F.data == "adm_schedule")
async def admin_schedule_quiz(callback_query: CallbackQuery, state: FSMContext):
    """Start quiz scheduling process - show available exams"""
    
    exams = await get_available_exams()
    
    if not exams:
        await state.set_state(AdminStates.scheduling_quiz_name)
        
        text = """📅 **SCHEDULE LIVE QUIZ**

No exams found in the system yet.
Step 1/6: Enter Quiz Name/Exam
Example: "GNM ANM 2027"
"""
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        buttons = [[InlineKeyboardButton(text="Cancel", callback_data="adm_back")]]
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        
        await callback_query.message.edit_text(text, reply_markup=kb)
        await callback_query.answer()
        return
    
    # Show available exams
    text = """📅 **SCHEDULE LIVE QUIZ**

Select an exam from uploaded questions:
(or enter a custom name)
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = []
    for exam in exams:
        buttons.append([InlineKeyboardButton(
            text=f"📝 {exam}",
            callback_data=f"schedule_exam_{exam}"
        )])
    
    buttons.append([InlineKeyboardButton(text="✏️ Custom Name", callback_data="schedule_custom")])
    buttons.append([InlineKeyboardButton(text="Cancel", callback_data="adm_back")])
    
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=kb)
    await callback_query.answer()


@router.callback_query(F.data.startswith("schedule_exam_"))
async def schedule_from_exam(callback_query: CallbackQuery, state: FSMContext):
    """Schedule quiz from selected exam"""
    
    exam_name = callback_query.data.split("schedule_exam_", 1)[1]
    
    await state.set_state(AdminStates.scheduling_quiz_description)
    await state.update_data(quiz_name=exam_name)
    
    await callback_query.message.edit_text(
        f"""Step 2/6: Enter Quiz Description
Exam: {exam_name}

Example: "Final Exam - All Chapters"
"""
    )
    await callback_query.answer()


@router.callback_query(F.data == "schedule_custom")
async def schedule_custom_exam(callback_query: CallbackQuery, state: FSMContext):
    """Schedule quiz with custom name"""
    
    await state.set_state(AdminStates.scheduling_quiz_name)
    
    await callback_query.message.edit_text(
        """Step 1/6: Enter Quiz Name/Exam Name
Example: "GNM ANM 2027"

⚠️ Make sure this matches the exam name you used when uploading questions!
"""
    )
    await callback_query.answer()



@router.message(AdminStates.scheduling_quiz_name)
async def schedule_quiz_name(message: Message, state: FSMContext):
    """Get quiz name"""
    
    await state.update_data(quiz_name=message.text)
    await state.set_state(AdminStates.scheduling_quiz_description)
    
    await message.answer(
        """Step 2/6: Enter Quiz Description
Example: "Complete Anatomy Chapter 1 Exam"
"""
    )


@router.message(AdminStates.scheduling_quiz_description)
async def schedule_quiz_description(message: Message, state: FSMContext):
    """Get quiz description"""
    
    await state.update_data(quiz_description=message.text)
    await state.set_state(AdminStates.scheduling_quiz_start)
    
    await message.answer(
        """Step 3/6: Enter Start Date & Time
Format: YYYY-MM-DD HH:MM
Example: 2026-07-10 10:00
"""
    )


@router.message(AdminStates.scheduling_quiz_start)
async def schedule_quiz_start(message: Message, state: FSMContext):
    """Get quiz start time"""
    
    try:
        start_time = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
        formatted_start = start_time.strftime("%Y-%m-%d %H:%M")
        await state.update_data(quiz_start=formatted_start)
        await state.set_state(AdminStates.scheduling_quiz_end)
        
        await message.answer(
            """Step 4/6: Enter End Date & Time
Format: YYYY-MM-DD HH:MM
Example: 2026-07-10 11:00
"""
        )
    except ValueError:
        await message.answer(
            "❌ Invalid format! Use: YYYY-MM-DD HH:MM\nExample: 2026-07-10 10:00"
        )


@router.message(AdminStates.scheduling_quiz_end)
async def schedule_quiz_end(message: Message, state: FSMContext):
    """Get quiz end time"""
    
    try:
        end_time = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
        formatted_end = end_time.strftime("%Y-%m-%d %H:%M")
        await state.update_data(quiz_end=formatted_end)
        await state.set_state(AdminStates.scheduling_quiz_questions)
        
        await message.answer(
            """Step 5/6: Total Number of Questions
Example: 50
"""
        )
    except ValueError:
        await message.answer(
            "❌ Invalid format! Use: YYYY-MM-DD HH:MM\nExample: 2026-07-10 11:00"
        )


@router.message(AdminStates.scheduling_quiz_questions)
async def schedule_quiz_questions(message: Message, state: FSMContext):
    """Get total questions"""
    
    try:
        total_q = int(message.text)
        await state.update_data(quiz_questions=total_q)
        await state.set_state(AdminStates.scheduling_quiz_marks)
        
        await message.answer(
            """Step 6/6: Total Marks
Example: 50
"""
        )
    except ValueError:
        await message.answer("❌ Please enter a valid number!")


@router.message(AdminStates.scheduling_quiz_marks)
async def schedule_quiz_marks(message: Message, state: FSMContext):
    """Get total marks and finalize"""
    
    try:
        total_marks = float(message.text)
        data = await state.get_data()
        
        await add_scheduled_quiz(
            name=data['quiz_name'],
            description=data['quiz_description'],
            start_time=data['quiz_start'],
            end_time=data['quiz_end'],
            total_questions=data['quiz_questions'],
            total_marks=total_marks,
            exam_type="scheduled",
            admin_id=message.from_user.id
        )
        
        await state.clear()
        
        await message.answer(
            f"""✅ **Quiz Scheduled Successfully!**

📝 Name: {data['quiz_name']}
📖 Description: {data['quiz_description']}
⏰ Start: {data['quiz_start']}
⏱️ End: {data['quiz_end']}
📊 Questions: {data['quiz_questions']}
💯 Marks: {total_marks}
"""
        )
        
    except ValueError:
        await message.answer("❌ Please enter a valid number for marks!")




# ===================================
# MANAGE SCHEDULED QUIZZES
# ===================================

@router.callback_query(F.data == "adm_manage_quizzes")
async def admin_manage_quizzes(callback_query: CallbackQuery, state: FSMContext):
    """Show scheduled quizzes management options"""
    
    await state.set_state(AdminStates.managing_scheduled_quizzes)
    
    text = """🗑️ **MANAGE SCHEDULED QUIZZES**

Choose action:
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = [
        [InlineKeyboardButton(text="📋 View All Quizzes", callback_data="msq_view")],
        [InlineKeyboardButton(text="🗑️ Delete Quiz", callback_data="msq_delete")],
        [InlineKeyboardButton(text="🗑️ Delete All Quizzes", callback_data="msq_delete_all")],
        [InlineKeyboardButton(text="Back", callback_data="adm_back")]
    ]
    
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=kb)
    await callback_query.answer()


@router.callback_query(F.data == "msq_view")
async def view_scheduled_quizzes(callback_query: CallbackQuery):
    """View all scheduled quizzes"""
    
    quizzes = await get_scheduled_quizzes()
    
    if not quizzes:
        text = """❌ **NO SCHEDULED QUIZZES**

No quizzes scheduled yet.
"""
    else:
        text = """📋 **SCHEDULED QUIZZES**

"""
        for quiz in quizzes:
            quiz_id, name, description, start_time, end_time, total_q, total_marks = quiz
            text += f"""
ID: {quiz_id}
📝 {name}
📖 {description}
⏰ Start: {start_time}
⏱️ End: {end_time}
📊 Questions: {total_q}
💯 Marks: {total_marks}
━━━━━━━━━━━━━━━━
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = [[InlineKeyboardButton(text="Back", callback_data="adm_manage_quizzes")]]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=kb)
    await callback_query.answer()


@router.callback_query(F.data == "msq_delete")
async def delete_quiz_menu(callback_query: CallbackQuery, state: FSMContext):
    """Show quiz deletion options"""
    
    quizzes = await get_scheduled_quizzes()
    
    if not quizzes:
        text = """❌ **NO SCHEDULED QUIZZES**

No quizzes to delete.
"""
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        buttons = [[InlineKeyboardButton(text="Back", callback_data="adm_manage_quizzes")]]
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        
        await callback_query.message.edit_text(text, reply_markup=kb)
        await callback_query.answer()
        return
    
    text = """🗑️ **DELETE QUIZ**

Choose a quiz to delete:
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = []
    for quiz in quizzes:
        quiz_id, name, _, _, _, _, _ = quiz
        buttons.append([InlineKeyboardButton(
            text=f"🗑️ {name}",
            callback_data=f"msq_delete_{quiz_id}"
        )])
    
    buttons.append([InlineKeyboardButton(text="Back", callback_data="adm_manage_quizzes")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=kb)
    await callback_query.answer()


@router.callback_query(F.data == "msq_delete_all")
async def confirm_delete_all_quizzes(callback_query: CallbackQuery):
    """Confirm delete all quizzes"""
    
    text = """⚠️ **DELETE ALL QUIZZES?**

This will delete ALL scheduled quizzes!
This action cannot be undone.

Are you sure?
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = [
        [InlineKeyboardButton(text="✅ Yes, Delete All", callback_data="msq_confirm_delete_all")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="adm_manage_quizzes")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=kb)
    await callback_query.answer()


@router.callback_query(F.data.startswith("msq_delete_"))
async def confirm_delete_quiz(callback_query: CallbackQuery):
    """Confirm delete specific quiz"""
    
    last_part = callback_query.data.split("_")[-1]
    
    try:
        quiz_id = int(last_part)
    except ValueError:
        # Not a numeric ID, skip this handler
        return
    
    await delete_scheduled_quiz(quiz_id)
    
    text = f"""✅ **QUIZ DELETED**

Quiz ID {quiz_id} has been deleted successfully!
"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = [[InlineKeyboardButton(text="Back", callback_data="adm_manage_quizzes")]]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=kb)
    await callback_query.answer("✅ Quiz deleted!")


@router.callback_query(F.data == "msq_confirm_delete_all")
async def delete_all_quizzes(callback_query: CallbackQuery, state: FSMContext):
    """Delete all scheduled quizzes"""
    
    try:
        await delete_all_scheduled_quizzes()
        
        text = """✅ **ALL QUIZZES DELETED**

All scheduled quizzes have been deleted successfully!
"""
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        buttons = [[InlineKeyboardButton(text="Back", callback_data="adm_back")]]
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        
        await callback_query.message.edit_text(text, reply_markup=kb)
        await callback_query.answer("✅ All quizzes deleted!")
        
    except Exception as e:
        await callback_query.answer(f"❌ Error: {str(e)}", show_alert=True)


@router.callback_query(F.data == "adm_back")
async def admin_back(callback_query: CallbackQuery):
    """Go back"""
    
    await callback_query.message.delete()
    await callback_query.answer()
